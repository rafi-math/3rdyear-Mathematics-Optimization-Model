"""Infeasibility diagnosis and elastic relaxation solver for plain-language conflict explanation."""
from __future__ import annotations

from typing import Dict, List, Optional, Tuple
import numpy as np
from scipy.optimize import linprog

from app.schemas import Plan
from app.solver.constraints import ProblemSetup, build_problem_setup


def check_cheap_infeasibility(plan: Plan, model_type: str = "B") -> Optional[Dict[str, List[str]]]:
    """Run fast checks for truly contradictory rule combinations. Minimums/maximums/locks are adjusted gracefully by the solver setup."""
    reasons: List[str] = []
    suggestions: List[str] = []

    try:
        # Build setup to validate course/rule references; setup also performs best-effort adjustments.
        build_problem_setup(plan, model_type)
    except Exception as e:
        return {
            "reasons": [str(e)],
            "suggestions": ["Check the course inputs and difficulty ratings."],
        }

    # Only flag contradictory dependency cycles that cannot be satisfied in general (x>=k*y and y>=m*x with k*m>1 => x=y=0 conflict if positives required).
    # We soften by letting solver attempt; report only clear mutual amplification conflicts.
    for r1 in plan.rules:
        if r1.enabled and r1.type == "dependency" and r1.course_id and r1.target_course_id:
            k1 = float(r1.dependency_k if r1.dependency_k is not None else 1.0)
            for r2 in plan.rules:
                if (
                    r2.enabled
                    and r2.type == "dependency"
                    and r2.course_id == r1.target_course_id
                    and r2.target_course_id == r1.course_id
                ):
                    k2 = float(r2.dependency_k if r2.dependency_k is not None else 1.0)
                    if k1 * k2 > 1.0 + 1e-4:
                        reasons.append(
                            f"Two rules conflict: '{r1.course_id}' and '{r1.target_course_id}' cannot both stay ahead of each other with those settings."
                        )
                        suggestions.append("Change or remove one of those 'keep ahead' rules.")
                        return {"reasons": reasons, "suggestions": suggestions}

    return None


def diagnose_infeasibility(plan: Plan, model_type: str = "B") -> Dict[str, List[str]]:
    """Diagnose infeasibility when LP cannot be solved, using cheap checks then elastic LP."""
    cheap = check_cheap_infeasibility(plan, model_type)
    if cheap is not None:
        return cheap

    reasons: List[str] = []
    suggestions: List[str] = []

    try:
        setup = build_problem_setup(plan, model_type)
        elastic_res = solve_elastic_lp(plan, setup)
        if elastic_res:
            reasons.extend(elastic_res[0])
            suggestions.extend(elastic_res[1])
        else:
            reasons.append("These rules cannot all hold simultaneously under the given budget.")
            suggestions.append("Try relaxing the most restrictive course minimums or upper limits.")
    except Exception as e:
        reasons.append(f"Model formulation conflict: {str(e)}")
        suggestions.append("Check active rules and bounds.")

    return {"reasons": reasons, "suggestions": suggestions}


def solve_elastic_lp(plan: Plan, setup: ProblemSetup) -> Optional[Tuple[List[str], List[str]]]:
    """Solve elastic problem adding penalty slack variables to identify conflicting constraints."""
    n = setup.n
    courses = plan.courses

    m_ineq = len(setup.additional_ineq_rows)
    p_tie = len(setup.tie_pairs)

    n_slacks = 1 + n + n + m_ineq + p_tie
    total_vars = n + n_slacks

    c_obj = np.zeros(total_vars, dtype=float)
    idx_v_budget = n
    idx_v_floor = n + 1
    idx_v_cap = n + 1 + n
    idx_v_ineq = n + 1 + 2 * n
    idx_v_tie = n + 1 + 2 * n + m_ineq

    c_obj[idx_v_budget] = 10.0
    for i in range(n):
        c_obj[idx_v_floor + i] = 5.0
        c_obj[idx_v_cap + i] = 5.0
    for j in range(m_ineq):
        c_obj[idx_v_ineq + j] = 1.0
    for k in range(p_tie):
        c_obj[idx_v_tie + k] = 2.0

    bounds = [(0.0, None) for _ in range(total_vars)]

    A_ub_list = []
    b_ub_list = []

    # Budget: sum(x_i) - v_budget <= budget
    row = np.zeros(total_vars, dtype=float)
    row[:n] = 1.0
    row[idx_v_budget] = -1.0
    A_ub_list.append(row)
    b_ub_list.append(setup.budget)

    # Floors: -x_i - v_floor_i <= -L_i
    for i in range(n):
        row = np.zeros(total_vars, dtype=float)
        row[i] = -1.0
        row[idx_v_floor + i] = -1.0
        A_ub_list.append(row)
        b_ub_list.append(-setup.floors[i])

    # Caps: x_i - v_cap_i <= U_i
    for i in range(n):
        if not np.isinf(setup.caps[i]):
            row = np.zeros(total_vars, dtype=float)
            row[i] = 1.0
            row[idx_v_cap + i] = -1.0
            A_ub_list.append(row)
            b_ub_list.append(setup.caps[i])

    # Additional user ineqs: row*x - v_ineq <= rhs
    for j in range(m_ineq):
        row = np.zeros(total_vars, dtype=float)
        row[:n] = setup.additional_ineq_rows[j]
        row[idx_v_ineq + j] = -1.0
        A_ub_list.append(row)
        b_ub_list.append(setup.additional_ineq_rhs[j])

    # Tie pairs: x_i - x_j - v_tie <= 0 and -x_i + x_j - v_tie <= 0
    for k, (i, j) in enumerate(setup.tie_pairs):
        row1 = np.zeros(total_vars, dtype=float)
        row1[i] = 1.0
        row1[j] = -1.0
        row1[idx_v_tie + k] = -1.0
        A_ub_list.append(row1)
        b_ub_list.append(0.0)

        row2 = np.zeros(total_vars, dtype=float)
        row2[i] = -1.0
        row2[j] = 1.0
        row2[idx_v_tie + k] = -1.0
        A_ub_list.append(row2)
        b_ub_list.append(0.0)

    res = linprog(
        c=c_obj,
        A_ub=np.array(A_ub_list),
        b_ub=np.array(b_ub_list),
        bounds=bounds,
        method="highs",
    )

    if not res.success:
        return None

    reasons: List[str] = []
    suggestions: List[str] = []

    sol = res.x
    if sol[idx_v_budget] > 1e-3:
        amount = sol[idx_v_budget]
        reasons.append(f"Budget is short by {amount:.1f} minutes to meet all course limits.")
        suggestions.append(f"Increase the budget by at least {amount:.1f} minutes.")

    for j in range(m_ineq):
        if sol[idx_v_ineq + j] > 1e-3:
            name = setup.additional_ineq_names[j]
            amount = sol[idx_v_ineq + j]
            reasons.append(f"Rule conflict: {name} (violated by {amount:.1f} minutes).")
            suggestions.append(f"Relax or disable the rule: '{name}'.")

    for i in range(n):
        if sol[idx_v_floor + i] > 1e-3:
            amount = sol[idx_v_floor + i]
            cname = courses[i].name
            reasons.append(f"Minimum requirement for '{cname}' cannot be met by {amount:.1f} minutes.")
            suggestions.append(f"Lower the minimum required time for '{cname}'.")

    for i in range(n):
        if sol[idx_v_cap + i] > 1e-3:
            amount = sol[idx_v_cap + i]
            cname = courses[i].name
            reasons.append(f"Upper bound on '{cname}' exceeded by {amount:.1f} minutes.")
            suggestions.append(f"Increase the maximum cap on '{cname}'.")

    return (reasons, suggestions) if reasons else None
