"""Multi-period schedule allocation splitting course totals across time periods."""
from __future__ import annotations

from typing import Dict, List, Optional
import numpy as np
from scipy.optimize import linprog

from app.schemas import Course, Period, PeriodSchedule, Plan, Rule


def schedule_multi_period(
    plan: Plan,
    course_totals: Dict[str, float],  # course_name -> total_minutes X_i
) -> List[PeriodSchedule]:
    """Split course totals across periods proportionally, respecting period budgets and rules."""
    courses = plan.courses
    n = len(courses)
    course_names = [c.name for c in courses]
    c_to_idx = {name: i for i, name in enumerate(course_names)}

    periods: List[Period] = []
    if plan.budget.mode == "custom" and plan.budget.periods:
        periods = plan.budget.periods
    elif plan.budget.mode == "daily":
        days = plan.budget.days_per_week if plan.budget.days_per_week is not None else 7
        daily_amount = plan.budget.amount_minutes or (plan.budget.total_minutes / days)
        day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        periods = [Period(label=day_names[d % 7], minutes=daily_amount) for d in range(days)]
    else:
        # Weekly mode: single period
        periods = [Period(label="Weekly allocation", minutes=plan.budget.total_minutes)]

    T = len(periods)
    if T == 1:
        return [
            PeriodSchedule(
                period_label=periods[0].label,
                budget_minutes=periods[0].minutes,
                allocations={name: course_totals.get(name, 0.0) for name in course_names},
            )
        ]

    period_budgets = np.array([p.minutes for p in periods], dtype=float)
    total_period_budget = float(np.sum(period_budgets))
    total_needed = float(sum(course_totals.get(name, 0.0) for name in course_names))

    if total_period_budget < total_needed - 1e-4:
        raise ValueError(
            f"Total time across periods ({total_period_budget:.1f} min) is less than the total allocated study time ({total_needed:.1f} min)."
        )

    # Variables:
    # y_{i, t} for i in 0..n-1, t in 0..T-1 (n * T variables)
    # e_{i, t} for i in 0..n-1, t in 0..T-1 (n * T variables)
    # Total variables = 2 * n * T
    num_vars = 2 * n * T

    def y_idx(i: int, t: int) -> int:
        return i * T + t

    def e_idx(i: int, t: int) -> int:
        return n * T + i * T + t

    # Objective: minimise sum_i sum_t e_{i, t}
    c_obj = np.zeros(num_vars, dtype=float)
    for i in range(n):
        for t in range(T):
            c_obj[e_idx(i, t)] = 1.0

    bounds = [(0.0, None) for _ in range(num_vars)]

    # Bounds on unavailable courses or period-specific locks
    for rule in plan.rules:
        if not rule.enabled:
            continue
        if rule.type == "unavailable" and rule.course_id and rule.period_label:
            c_idx = c_to_idx.get(rule.course_id)
            for t, p in enumerate(periods):
                if p.label.strip().lower() == rule.period_label.strip().lower() and c_idx is not None:
                    bounds[y_idx(c_idx, t)] = (0.0, 0.0)
        elif rule.type == "lock" and rule.course_id and rule.period_label and rule.time_minutes is not None:
            c_idx = c_to_idx.get(rule.course_id)
            for t, p in enumerate(periods):
                if p.label.strip().lower() == rule.period_label.strip().lower() and c_idx is not None:
                    val = float(rule.time_minutes)
                    bounds[y_idx(c_idx, t)] = (val, val)

    A_eq_list = []
    b_eq_list = []

    # Constraint: sum_t y_{i, t} = X_i for each course i
    for i, name in enumerate(course_names):
        X_i = course_totals.get(name, 0.0)
        row = np.zeros(num_vars, dtype=float)
        for t in range(T):
            row[y_idx(i, t)] = 1.0
        A_eq_list.append(row)
        b_eq_list.append(X_i)

    A_ub_list = []
    b_ub_list = []

    # Constraint: sum_i y_{i, t} <= b_t for each period t
    for t in range(T):
        row = np.zeros(num_vars, dtype=float)
        for i in range(n):
            row[y_idx(i, t)] = 1.0
        A_ub_list.append(row)
        b_ub_list.append(period_budgets[t])

    # Absolute value constraints for e_{i, t}:
    # target_{i, t} = X_i * b_t / total_period_budget
    # e_{i, t} >= y_{i, t} - target_{i, t}  =>  y_{i, t} - e_{i, t} <= target_{i, t}
    # e_{i, t} >= -y_{i, t} + target_{i, t} => -y_{i, t} - e_{i, t} <= -target_{i, t}
    for i, name in enumerate(course_names):
        X_i = course_totals.get(name, 0.0)
        for t in range(T):
            target = (X_i * period_budgets[t] / total_period_budget) if total_period_budget > 0 else 0.0

            # y - e <= target
            row1 = np.zeros(num_vars, dtype=float)
            row1[y_idx(i, t)] = 1.0
            row1[e_idx(i, t)] = -1.0
            A_ub_list.append(row1)
            b_ub_list.append(target)

            # -y - e <= -target
            row2 = np.zeros(num_vars, dtype=float)
            row2[y_idx(i, t)] = -1.0
            row2[e_idx(i, t)] = -1.0
            A_ub_list.append(row2)
            b_ub_list.append(-target)

    res = linprog(
        c=c_obj,
        A_ub=np.array(A_ub_list),
        b_ub=np.array(b_ub_list),
        A_eq=np.array(A_eq_list),
        b_eq=np.array(b_eq_list),
        bounds=bounds,
        method="highs",
    )

    if not res.success:
        # Fallback to simple proportional rounding if LP fails due to restrictive bounds
        schedules: List[PeriodSchedule] = []
        for t, p in enumerate(periods):
            p_allocs: Dict[str, float] = {}
            for i, name in enumerate(course_names):
                X_i = course_totals.get(name, 0.0)
                p_allocs[name] = round(X_i * period_budgets[t] / total_period_budget, 1)
            schedules.append(
                PeriodSchedule(
                    period_label=p.label,
                    budget_minutes=p.minutes,
                    allocations=p_allocs,
                )
            )
        return schedules

    schedules: List[PeriodSchedule] = []
    sol = res.x
    for t, p in enumerate(periods):
        p_allocs: Dict[str, float] = {}
        for i, name in enumerate(course_names):
            p_allocs[name] = float(sol[y_idx(i, t)])
        schedules.append(
            PeriodSchedule(
                period_label=p.label,
                budget_minutes=p.minutes,
                allocations=p_allocs,
            )
        )

    return schedules
