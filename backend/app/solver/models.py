"""Linear programming solvers for Model A, Model B, and Model C using scipy.optimize.linprog (HiGHS)."""
from __future__ import annotations

import time
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
from scipy.optimize import linprog

from app.schemas import (
    CourseAllocation,
    ModelResult,
    ModelType,
    Plan,
)
from app.solver.constraints import (
    ProblemSetup,
    build_problem_setup,
)
from app.solver.sensitivity import (
    analyze_sensitivity,
)


def solve_lp(
    plan: Plan,
    model_type: ModelType,
    setup: Optional[ProblemSetup] = None,
    budget_override: Optional[float] = None,
    fixed_bounds: Optional[Tuple[np.ndarray, np.ndarray]] = None,
) -> Dict[str, Any]:
    """Solve LP with HiGHS for Model A, B, or C."""
    if setup is None:
        setup = build_problem_setup(plan, model_type)

    n = setup.n
    budget = budget_override if budget_override is not None else setup.budget

    if fixed_bounds is not None:
        floors, caps = fixed_bounds
    else:
        floors, caps = setup.floors, setup.caps

    if model_type in ("A", "B"):
        # Variables: x_i for i in 0..n-1
        # Objective in hours: minimize -(weights / 60) * x
        c_obj = -setup.weights / 60.0

        bounds = []
        for i in range(n):
            lb = floors[i]
            ub = caps[i] if not np.isinf(caps[i]) else None
            bounds.append((lb, ub))

        # Inequality constraints: A_ub * x <= b_ub
        # Row 0: budget constraint sum(x_i) <= budget
        A_ub_list = [np.ones(n, dtype=float)]
        b_ub_list = [budget]
        ineq_labels = ["Budget constraint C1 (total study time <= budget)"]

        # Additional ineqs
        for row, rhs, name in zip(setup.additional_ineq_rows, setup.additional_ineq_rhs, setup.additional_ineq_names):
            A_ub_list.append(row)
            b_ub_list.append(rhs)
            ineq_labels.append(name)

        A_ub = np.array(A_ub_list, dtype=float)
        b_ub = np.array(b_ub_list, dtype=float)

        # Equality constraints: A_eq * x == b_eq
        A_eq_list = []
        b_eq_list = []
        eq_labels = []

        # Tie pairs C4
        for i, j in setup.tie_pairs:
            row = np.zeros(n, dtype=float)
            row[i] = 1.0
            row[j] = -1.0
            A_eq_list.append(row)
            b_eq_list.append(0.0)
            eq_labels.append(f"Tie-break C4: {setup.courses[i].course.name} == {setup.courses[j].course.name}")

        for row, rhs, name in zip(setup.additional_eq_rows, setup.additional_eq_rhs, setup.additional_eq_names):
            A_eq_list.append(row)
            b_eq_list.append(rhs)
            eq_labels.append(name)

        A_eq = np.array(A_eq_list, dtype=float) if A_eq_list else None
        b_eq = np.array(b_eq_list, dtype=float) if b_eq_list else None

        start_time = time.perf_counter()
        res = linprog(
            c=c_obj,
            A_ub=A_ub,
            b_ub=b_ub,
            A_eq=A_eq,
            b_eq=b_eq,
            bounds=bounds,
            method="highs",
        )
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        if not res.success:
            return {
                "success": False,
                "status": res.status,
                "message": res.message,
                "wall_time_ms": elapsed_ms,
                "setup": setup,
            }

        allocations_x = res.x
        objective_val = -res.fun  # convert back from minimization

        # Dual value of budget row (row 0 in ineqlin)
        # In HiGHS, marginal of Ax <= b is non-positive for minimization.
        budget_dual = 0.0
        if hasattr(res, "ineqlin") and res.ineqlin is not None and hasattr(res.ineqlin, "marginals"):
            if len(res.ineqlin.marginals) > 0:
                budget_dual = float(abs(res.ineqlin.marginals[0]))

        return {
            "success": True,
            "status": "optimal",
            "allocations": allocations_x,
            "objective_value": objective_val,
            "wall_time_ms": elapsed_ms,
            "setup": setup,
            "budget_dual": budget_dual,
            "A_ub": A_ub,
            "b_ub": b_ub,
            "ineq_labels": ineq_labels,
            "A_eq": A_eq,
            "b_eq": b_eq,
            "eq_labels": eq_labels,
            "bounds": bounds,
            "res": res,
        }

    else:
        # Model C: Piecewise-linear diminishing returns
        # Variables: [x_0..x_{n-1}, s_{0,0}..s_{0,K-1}, ..., s_{n-1,0}..s_{n-1,K-1}]
        # K = 3
        # lengths l = (60, 60, inf)
        # factors phi = (1.0, 0.6, 0.3)
        lengths = list(plan.settings.diminishing_lengths)
        factors = list(plan.settings.diminishing_factors)
        K = len(factors)
        while len(lengths) < K - 1:
            lengths.append(60.0)

        num_vars = n + n * K
        c_obj = np.zeros(num_vars, dtype=float)

        # Bounds
        bounds = []
        # For x_i: [floors[i], caps[i]]
        for i in range(n):
            lb = floors[i]
            ub = caps[i] if not np.isinf(caps[i]) else None
            bounds.append((lb, ub))

        # For s_{ik}:
        for i in range(n):
            for k in range(K):
                ub_k = lengths[k] if k < len(lengths) else None
                bounds.append((0.0, ub_k))
                var_idx = n + i * K + k
                # Objective in hours: maximize sum_i sum_k (w_i * phi_k / 60) * s_ik
                c_obj[var_idx] = -setup.weights[i] * factors[k] / 60.0

        # Equalities:
        # 1) x_i - sum_k s_{ik} = floors[i]
        A_eq_list = []
        b_eq_list = []
        eq_labels = []

        for i in range(n):
            row = np.zeros(num_vars, dtype=float)
            row[i] = 1.0
            for k in range(K):
                row[n + i * K + k] = -1.0
            A_eq_list.append(row)
            b_eq_list.append(floors[i])
            eq_labels.append(f"Model C segment definition for {setup.courses[i].course.name}")

        # 2) Tie-break C4: x_i - x_j = 0
        for i, j in setup.tie_pairs:
            row = np.zeros(num_vars, dtype=float)
            row[i] = 1.0
            row[j] = -1.0
            A_eq_list.append(row)
            b_eq_list.append(0.0)
            eq_labels.append(f"Tie-break C4: {setup.courses[i].course.name} == {setup.courses[j].course.name}")

        # Additional equality constraints from setup
        for orig_row, rhs, name in zip(setup.additional_eq_rows, setup.additional_eq_rhs, setup.additional_eq_names):
            row = np.zeros(num_vars, dtype=float)
            row[:n] = orig_row
            A_eq_list.append(row)
            b_eq_list.append(rhs)
            eq_labels.append(name)

        # Inequalities:
        # Row 0: budget constraint sum(x_i) <= budget
        A_ub_list = []
        b_ub_list = []
        ineq_labels = []

        budget_row = np.zeros(num_vars, dtype=float)
        budget_row[:n] = 1.0
        A_ub_list.append(budget_row)
        b_ub_list.append(budget)
        ineq_labels.append("Budget constraint C1 (total study time <= budget)")

        # Additional ineqs
        for orig_row, rhs, name in zip(setup.additional_ineq_rows, setup.additional_ineq_rhs, setup.additional_ineq_names):
            row = np.zeros(num_vars, dtype=float)
            row[:n] = orig_row
            A_ub_list.append(row)
            b_ub_list.append(rhs)
            ineq_labels.append(name)

        A_ub = np.array(A_ub_list, dtype=float)
        b_ub = np.array(b_ub_list, dtype=float)
        A_eq = np.array(A_eq_list, dtype=float)
        b_eq = np.array(b_eq_list, dtype=float)

        start_time = time.perf_counter()
        res = linprog(
            c=c_obj,
            A_ub=A_ub,
            b_ub=b_ub,
            A_eq=A_eq,
            b_eq=b_eq,
            bounds=bounds,
            method="highs",
        )
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        if not res.success:
            return {
                "success": False,
                "status": res.status,
                "message": res.message,
                "wall_time_ms": elapsed_ms,
                "setup": setup,
            }

        allocations_x = res.x[:n]
        # Include baseline value of floors in objective value for reporting (in hours)
        base_floor_value = float(np.sum(setup.weights * floors)) / 60.0
        objective_val = base_floor_value - res.fun

        budget_dual = 0.0
        if hasattr(res, "ineqlin") and res.ineqlin is not None and hasattr(res.ineqlin, "marginals"):
            if len(res.ineqlin.marginals) > 0:
                budget_dual = float(abs(res.ineqlin.marginals[0]))

        return {
            "success": True,
            "status": "optimal",
            "allocations": allocations_x,
            "objective_value": objective_val,
            "wall_time_ms": elapsed_ms,
            "setup": setup,
            "budget_dual": budget_dual,
            "A_ub": A_ub,
            "b_ub": b_ub,
            "ineq_labels": ineq_labels,
            "A_eq": A_eq,
            "b_eq": b_eq,
            "eq_labels": eq_labels,
            "bounds": bounds,
            "res": res,
        }


def build_model_result(plan: Plan, model_type: ModelType) -> ModelResult:
    """Solve model and build the structured ModelResult including sensitivity and diagnostics."""
    setup = build_problem_setup(plan, model_type)
    solve_data = solve_lp(plan, model_type, setup=setup)

    if not solve_data["success"]:
        raise ValueError(f"Solver failed for Model {model_type}: {solve_data.get('message')}")

    allocations_x = solve_data["allocations"]
    n = setup.n

    # Classify each course status
    allocations_list: List[CourseAllocation] = []
    min_alloc = float(np.min(allocations_x)) if n > 0 else 0.0
    max_alloc = float(np.max(allocations_x)) if n > 0 else 0.0

    for i in range(n):
        rc = setup.courses[i]
        val = float(allocations_x[i])
        floor = float(setup.floors[i])
        cap = float(setup.caps[i]) if not np.isinf(setup.caps[i]) else None

        if rc.is_locked:
            status = "locked"
        elif abs(val - floor) <= 1e-4:
            status = "at_minimum"
        elif cap is not None and abs(val - cap) <= 1e-4:
            if rc.has_custom_bounds and (rc.course.max_minutes is not None or any(r.type == "max" and r.course_id == rc.course.name for r in plan.rules if r.enabled)):
                status = "at_user_maximum"
            else:
                status = "at_cap"
        else:
            status = "free"

        allocations_list.append(
            CourseAllocation(
                course_name=rc.course.name,
                minutes=val,
                weight=float(setup.weights[i]),
                cap=cap,
                floor=floor,
                status=status,
                is_min_allocation=abs(val - min_alloc) <= 1e-4,
                is_max_allocation=abs(val - max_alloc) <= 1e-4,
            )
        )

    # Perform sensitivity analysis
    sens = analyze_sensitivity(plan, model_type, setup, solve_data)

    return ModelResult(
        model=model_type,
        allocations=allocations_list,
        total_minutes=float(np.sum(allocations_x)),
        objective_value=float(solve_data["objective_value"]),
        solver_status="optimal",
        wall_time_ms=float(solve_data["wall_time_ms"]),
        shadow_price=sens["shadow_price"],
        shadow_price_delta_check=sens["delta_check"],
        shadow_price_check_valid=sens["check_valid"],
        next_hour_courses=sens["next_hour_courses"],
        constraints=sens["constraints"],
        tie_breaks_skipped=setup.tie_breaks_skipped,
    )
