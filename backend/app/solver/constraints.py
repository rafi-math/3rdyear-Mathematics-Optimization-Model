"""Shared constraint builders and parameters for models A, B, and C."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple
import numpy as np

from app.schemas import (
    Course,
    Plan,
    Rule,
    DIFFICULTY_COEFFICIENTS,
)


@dataclass
class ResolvedCourse:
    index: int
    course: Course
    weight: float
    floor: float
    cap: Optional[float]
    is_locked: bool
    locked_value: Optional[float]
    has_custom_bounds: bool


@dataclass
class ProblemSetup:
    n: int
    courses: List[ResolvedCourse]
    budget: float
    weights: np.ndarray
    floors: np.ndarray
    caps: np.ndarray  # could be inf for Model C or uncapped
    tie_pairs: List[Tuple[int, int]]
    tie_breaks_skipped: List[str]
    additional_ineq_rows: List[np.ndarray] = field(default_factory=list)
    additional_ineq_rhs: List[float] = field(default_factory=list)
    additional_ineq_names: List[str] = field(default_factory=list)
    additional_eq_rows: List[np.ndarray] = field(default_factory=list)
    additional_eq_rhs: List[float] = field(default_factory=list)
    additional_eq_names: List[str] = field(default_factory=list)


def match_course(identifier: Optional[str], courses: List[Course]) -> Optional[int]:
    """Find course index by id or case-insensitive name."""
    if not identifier:
        return None
    ident = identifier.strip().lower()
    for idx, c in enumerate(courses):
        if c.id and c.id.strip().lower() == ident:
            return idx
        if c.name.strip().lower() == ident:
            return idx
    return None


def get_course_difficulty(course: Course, treat_unassigned_as_easiest: bool, multipliers: Optional[Dict[str, float]] = None) -> float:
    """Return course difficulty multiplier or raise ValueError if unassigned and not allowed."""
    if course.custom_difficulty is not None:
        return float(course.custom_difficulty)
    coeffs = multipliers or DIFFICULTY_COEFFICIENTS
    if course.difficulty_level is not None:
        return float(coeffs.get(course.difficulty_level, DIFFICULTY_COEFFICIENTS[course.difficulty_level]))
    if treat_unassigned_as_easiest:
        return float(coeffs.get("easiest", 0.8))
    raise ValueError(f"Course '{course.name}' has no difficulty assigned.")


def compute_weights(plan: Plan, model_type: str) -> np.ndarray:
    """Compute weights for each course under Model A, B, or C."""
    n = len(plan.courses)
    weights = np.zeros(n, dtype=float)

    # Priority boosts from rules
    boosts = {i: 1.0 for i in range(n)}
    for rule in plan.rules:
        if rule.enabled and rule.type == "boost" and rule.boost_factor is not None:
            idx = match_course(rule.course_id, plan.courses)
            if idx is not None:
                boosts[idx] = float(rule.boost_factor)

    multipliers = getattr(plan.settings, "difficulty_multipliers", None) or DIFFICULTY_COEFFICIENTS
    for i, c in enumerate(plan.courses):
        credits = float(c.credits)
        p_i = boosts[i]
        if model_type == "A":
            weights[i] = credits * p_i
        else:  # B and C
            d_i = get_course_difficulty(c, plan.settings.treat_unassigned_as_easiest, multipliers)
            weights[i] = credits * d_i * p_i

    return weights


def _scale_to_budget(values: np.ndarray, limit: float, caps: Optional[np.ndarray] = None) -> np.ndarray:
    """Scale positive values down proportionally so sum(values) <= limit, respecting caps."""
    vals = np.maximum(values.astype(float), 0.0)
    if caps is not None:
        vals = np.minimum(vals, np.maximum(caps.astype(float), 0.0))
    total = float(np.sum(vals))
    if total <= limit + 1e-9 or total <= 0:
        return vals
    scale = max(0.0, limit) / total
    vals = vals * scale
    if caps is not None:
        vals = np.minimum(vals, np.maximum(caps.astype(float), 0.0))
        # iterative fix for rounding/cap saturation
        for _ in range(5):
            total = float(np.sum(vals))
            if total <= limit + 1e-9:
                break
            free = vals < (np.maximum(caps.astype(float), 0.0) - 1e-9)
            free_sum = float(np.sum(vals[free]))
            if free_sum <= 1e-9:
                break
            scale = max(0.0, limit - float(np.sum(vals[~free]))) / free_sum
            vals[free] = vals[free] * scale
            vals = np.minimum(vals, np.maximum(caps.astype(float), 0.0))
    return vals


def build_problem_setup(plan: Plan, model_type: str) -> ProblemSetup:
    """Construct bounds, tie-breaks, and additional constraints with graceful feasibility adjustments."""
    courses = plan.courses
    n = len(courses)
    budget = float(max(plan.budget.total_minutes, 0.0))
    f_global = float(max(plan.settings.min_minutes_per_course, 0.0))

    weights = compute_weights(plan, model_type)

    # Track user-specified custom bounds/locks
    user_mins: Dict[int, float] = {}
    user_maxs: Dict[int, float] = {}
    user_locks: Dict[int, float] = {}
    courses_with_custom_bounds: Set[int] = set()

    for i, c in enumerate(courses):
        if c.locked_minutes is not None:
            user_locks[i] = float(max(c.locked_minutes, 0.0))
            courses_with_custom_bounds.add(i)
        if c.min_minutes is not None:
            user_mins[i] = float(max(c.min_minutes, 0.0))
            courses_with_custom_bounds.add(i)
        if c.max_minutes is not None:
            user_maxs[i] = float(max(c.max_minutes, 0.0))
            courses_with_custom_bounds.add(i)

    # Process rules
    for rule in plan.rules:
        if not rule.enabled:
            continue
        idx = match_course(rule.course_id, courses)
        if idx is not None:
            if rule.type == "lock" and rule.time_minutes is not None:
                user_locks[idx] = float(max(rule.time_minutes, 0.0))
                courses_with_custom_bounds.add(idx)
            elif rule.type == "min" and rule.time_minutes is not None:
                user_mins[idx] = max(user_mins.get(idx, 0.0), float(max(rule.time_minutes, 0.0)))
                courses_with_custom_bounds.add(idx)
            elif rule.type == "max" and rule.time_minutes is not None:
                val = float(max(rule.time_minutes, 0.0))
                user_maxs[idx] = min(user_maxs[idx], val) if idx in user_maxs else val
                courses_with_custom_bounds.add(idx)

    # Raw floors/caps
    raw_floors = np.zeros(n, dtype=float)
    raw_caps = np.full(n, np.inf, dtype=float)
    is_locked_arr = np.zeros(n, dtype=bool)

    for i in range(n):
        if i in user_locks:
            is_locked_arr[i] = True
            raw_floors[i] = user_locks[i]
            raw_caps[i] = user_locks[i]
        else:
            raw_floors[i] = max(f_global, user_mins.get(i, 0.0))
            if i in user_maxs:
                raw_caps[i] = user_maxs[i]

    # Ensure floors do not exceed caps (user min > max): clamp floor to cap gracefully
    finite_cap_mask = ~np.isinf(raw_caps)
    raw_floors[finite_cap_mask] = np.minimum(raw_floors[finite_cap_mask], raw_caps[finite_cap_mask])

    floors = raw_floors.copy()
    caps = raw_caps.copy()

    # Gracefully fit minimums/locks into budget (best-effort, no hard error)
    locked_idx = np.where(is_locked_arr)[0]
    unlocked_idx = np.where(~is_locked_arr)[0]

    if locked_idx.size > 0:
        locked_sum = float(np.sum(floors[locked_idx]))
        if locked_sum > budget + 1e-9 and locked_sum > 0:
            scaled_locked = floors[locked_idx] * (budget / locked_sum)
            floors[locked_idx] = scaled_locked
            caps[locked_idx] = scaled_locked
        remaining = max(0.0, budget - float(np.sum(floors[locked_idx])))
    else:
        remaining = budget

    if unlocked_idx.size > 0:
        unlocked_floors = floors[unlocked_idx]
        unlocked_caps = caps[unlocked_idx]
        unlocked_sum = float(np.sum(unlocked_floors))
        if unlocked_sum > remaining + 1e-9:
            # allow scaling below global floor to satisfy budget (best-effort)
            scaled = _scale_to_budget(unlocked_floors, remaining, unlocked_caps)
            floors[unlocked_idx] = scaled

    # Final safety clamps
    floors = np.maximum(floors, 0.0)
    finite_caps = ~np.isinf(caps)
    floors[finite_caps] = np.minimum(floors[finite_caps], caps[finite_caps])
    # If total still exceeds budget due to caps saturation (rare), scale everything down
    total_floors = float(np.sum(floors))
    if total_floors > budget + 1e-6 and total_floors > 0:
        floors = floors * (budget / total_floors)
        # keep locks consistent with caps
        if locked_idx.size > 0:
            caps[locked_idx] = floors[locked_idx]

    resolved_courses: List[ResolvedCourse] = []
    for i, c in enumerate(courses):
        floor_val = float(floors[i])
        cap_val = float(caps[i])
        is_locked = bool(is_locked_arr[i]) and abs(floor_val - cap_val) <= 1e-6
        resolved_courses.append(
            ResolvedCourse(
                index=i,
                course=c,
                weight=float(weights[i]),
                floor=floor_val,
                cap=cap_val if not np.isinf(cap_val) else None,
                is_locked=is_locked,
                locked_value=floor_val if is_locked else (user_locks.get(i) if i in user_locks else None),
                has_custom_bounds=i in courses_with_custom_bounds,
            )
        )

    # Tie-breaking equality constraints C4
    tie_pairs: List[Tuple[int, int]] = []
    tie_breaks_skipped: List[str] = []

    if plan.settings.tie_break:
        for i in range(n):
            for j in range(i + 1, n):
                wi, wj = weights[i], weights[j]
                max_w = max(wi, wj)
                if max_w > 0 and abs(wi - wj) <= 1e-9 * max_w:
                    # Check if either course has custom bounds/min/max/lock
                    if i in courses_with_custom_bounds or j in courses_with_custom_bounds:
                        tie_breaks_skipped.append(
                            f"{courses[i].name} and {courses[j].name} (equal weight {wi:.2f}, but course rules applied)"
                        )
                    else:
                        tie_pairs.append((i, j))

    # Additional linear rules
    add_ineq_rows: List[np.ndarray] = []
    add_ineq_rhs: List[float] = []
    add_ineq_names: List[str] = []

    add_eq_rows: List[np.ndarray] = []
    add_eq_rhs: List[float] = []
    add_eq_names: List[str] = []

    for rule in plan.rules:
        if not rule.enabled:
            continue
        if rule.type == "dependency" and rule.course_id and rule.target_course_id:
            idx_a = match_course(rule.course_id, courses)
            idx_b = match_course(rule.target_course_id, courses)
            if idx_a is not None and idx_b is not None:
                k = float(rule.dependency_k if rule.dependency_k is not None else 1.0)
                # x_A >= k * x_B  =>  -x_A + k * x_B <= 0
                row = np.zeros(n, dtype=float)
                row[idx_a] = -1.0
                row[idx_b] = k
                add_ineq_rows.append(row)
                add_ineq_rhs.append(0.0)
                add_ineq_names.append(
                    f"Dependency: {courses[idx_a].name} >= {k} * {courses[idx_b].name}"
                )
        elif rule.type == "group_limit" and rule.group_course_ids and rule.time_minutes is not None:
            indices = [
                match_course(cid, courses)
                for cid in rule.group_course_ids
                if match_course(cid, courses) is not None
            ]
            if indices:
                row = np.zeros(n, dtype=float)
                for idx in indices:
                    row[idx] = 1.0
                limit = float(rule.time_minutes)
                add_ineq_rows.append(row)
                add_ineq_rhs.append(limit)
                group_names = ", ".join(courses[i].name for i in indices)
                add_ineq_names.append(f"Group limit on [{group_names}] <= {limit} min")

    return ProblemSetup(
        n=n,
        courses=resolved_courses,
        budget=budget,
        weights=weights,
        floors=floors,
        caps=caps,
        tie_pairs=tie_pairs,
        tie_breaks_skipped=tie_breaks_skipped,
        additional_ineq_rows=add_ineq_rows,
        additional_ineq_rhs=add_ineq_rhs,
        additional_ineq_names=add_ineq_names,
        additional_eq_rows=add_eq_rows,
        additional_eq_rhs=add_eq_rhs,
        additional_eq_names=add_eq_names,
    )
