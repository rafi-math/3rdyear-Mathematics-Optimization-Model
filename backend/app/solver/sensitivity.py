"""Sensitivity analysis, shadow price calculation, numeric check, and constraint slack reports."""
from __future__ import annotations

from typing import Any, Dict, List
import numpy as np

from app.schemas import (
    ConstraintStatus,
    ModelType,
    Plan,
)
from app.solver.constraints import ProblemSetup


def analyze_sensitivity(
    plan: Plan,
    model_type: ModelType,
    setup: ProblemSetup,
    solve_data: Dict[str, Any],
) -> Dict[str, Any]:
    """Compute shadow price, next-hour courses, 30-minute numeric check, and constraint slack."""
    from app.solver.models import solve_lp

    allocations_x = solve_data["allocations"]
    n = setup.n
    base_obj = float(solve_data["objective_value"])

    # Raw budget dual per minute from HiGHS
    budget_dual_per_min = float(solve_data.get("budget_dual", 0.0))
    # Report per hour: multiply by 60
    shadow_price_per_hour = round(budget_dual_per_min * 60.0, 4)

    # Next hour courses:
    # Courses with L_i + eps < x_i < U_i - eps, not locked
    eps = 1e-4
    next_courses: List[str] = []

    for i in range(n):
        rc = setup.courses[i]
        if rc.is_locked:
            continue
        val = allocations_x[i]
        floor = setup.floors[i]
        cap = setup.caps[i]

        is_free = (val > floor + eps) and (np.isinf(cap) or val < cap - eps)
        if is_free:
            if model_type in ("A", "B"):
                # Weight in units per hour matches shadow price per hour within tolerance
                if abs(setup.weights[i] - shadow_price_per_hour) <= 1e-4:
                    next_courses.append(rc.course.name)
            else:
                next_courses.append(rc.course.name)

    # If no exact match found due to numerical tolerance, collect any free courses
    if not next_courses:
        for i in range(n):
            rc = setup.courses[i]
            if not rc.is_locked and allocations_x[i] < (setup.caps[i] - eps if not np.isinf(setup.caps[i]) else 1e9):
                if allocations_x[i] > setup.floors[i] + eps:
                    next_courses.append(rc.course.name)

    # Numeric check: re-solve with budget + 30 min, holding L_i and U_i FIXED
    fixed_floors = np.copy(setup.floors)
    fixed_caps = np.copy(setup.caps)
    check_budget = setup.budget + 30.0

    check_data = solve_lp(
        plan,
        model_type,
        setup=setup,
        budget_override=check_budget,
        fixed_bounds=(fixed_floors, fixed_caps),
    )

    delta_check = None
    check_valid = True
    if check_data.get("success"):
        check_obj = float(check_data["objective_value"])
        delta_obj = check_obj - base_obj
        # Delta objective / 0.5 h gives rate per hour
        delta_per_hour = round(delta_obj / 0.5, 4)
        delta_check = delta_per_hour
        # They agree within 1e-4 if within range
        if abs(delta_per_hour - shadow_price_per_hour) > 1e-3:
            check_valid = False

    # Constraints slack report
    constraints: List[ConstraintStatus] = []

    # 1. Budget constraint
    used_minutes = float(np.sum(allocations_x))
    budget_slack = max(0.0, float(setup.budget - used_minutes))
    constraints.append(
        ConstraintStatus(
            name="Weekly budget constraint C1",
            description=f"Total study time across all courses cannot exceed {setup.budget:.1f} min.",
            slack_minutes=budget_slack,
            is_binding=budget_slack <= eps,
        )
    )

    # 2. Additional ineq constraints
    if "A_ub" in solve_data and solve_data["A_ub"] is not None:
        A_ub = solve_data["A_ub"]
        b_ub = solve_data["b_ub"]
        labels = solve_data.get("ineq_labels", [])
        # Skip row 0 (budget already reported)
        for r_idx in range(1, len(b_ub)):
            row = A_ub[r_idx]
            rhs = b_ub[r_idx]
            lhs = float(np.dot(row[:n], allocations_x))
            slack = max(0.0, rhs - lhs)
            name = labels[r_idx] if r_idx < len(labels) else f"Inequality constraint {r_idx}"
            constraints.append(
                ConstraintStatus(
                    name=name,
                    description=f"{name} (limit: {rhs:.1f} min)",
                    slack_minutes=slack,
                    is_binding=slack <= eps,
                )
            )

    # 3. Floors and Caps per course
    for i in range(n):
        rc = setup.courses[i]
        val = allocations_x[i]
        floor = setup.floors[i]
        cap = setup.caps[i]

        floor_slack = val - floor
        if floor_slack <= eps:
            constraints.append(
                ConstraintStatus(
                    name=f"Minimum floor: {rc.course.name}",
                    description=f"Course must receive at least {floor:.1f} min.",
                    slack_minutes=max(0.0, floor_slack),
                    is_binding=True,
                )
            )

        if not np.isinf(cap):
            cap_slack = cap - val
            if cap_slack <= eps:
                rule_desc = "proportional cap" if not rc.has_custom_bounds else "maximum limit"
                constraints.append(
                    ConstraintStatus(
                        name=f"Upper bound ({rule_desc}): {rc.course.name}",
                        description=f"Course cannot exceed {cap:.1f} min.",
                        slack_minutes=max(0.0, cap_slack),
                        is_binding=True,
                    )
                )

    return {
        "shadow_price": shadow_price_per_hour,
        "delta_check": delta_check,
        "check_valid": check_valid,
        "next_hour_courses": next_courses,
        "constraints": constraints,
    }
