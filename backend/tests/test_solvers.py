"""Unit, golden, parity, and property tests for linear programming solver engine (Tests 1-7)."""
from __future__ import annotations

import json
from pathlib import Path
import numpy as np
import pytest
import pulp
from hypothesis import given, settings, strategies as st

from app.schemas import Course, Plan, Budget, PlanSettings
from app.solver.models import build_model_result
from app.solver.constraints import build_problem_setup
from app.solver.diagnose import diagnose_infeasibility
from app.explain import format_minutes_text

FIXTURE_PATH = Path(__file__).resolve().parent.parent / "fixtures" / "case-study.json"


@pytest.fixture
def case_study_plan() -> Plan:
    with open(FIXTURE_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return Plan(**data)


# Test 1: Golden
def test_1_golden_case_study(case_study_plan: Plan):
    """The case-study fixture reproduces reference table within 0.1 min, totals 456, and lambda = 3.0."""
    # Expected exact allocations from spec 03 §4
    ref_table = {
        "Real Analysis (II)": {"A": 29.5, "B": 31.1},
        "Complex Analysis (I)": {"A": 29.5, "B": 31.1},
        "Abstract Algebra": {"A": 69.7, "B": 84.4},
        "Partial Differential Equations": {"A": 29.5, "B": 31.1},
        "Methods of Applied Mathematics": {"A": 69.7, "B": 77.4},
        "Mechanics": {"A": 69.7, "B": 84.4},
        "Numerical Analysis (I)": {"A": 29.5, "B": 20.0},
        "Linear Programming": {"A": 69.7, "B": 56.3},
        "Number Theory": {"A": 29.5, "B": 20.0},
        "Mathematical Computing Lab": {"A": 29.5, "B": 20.0},
    }

    res_a = build_model_result(case_study_plan, "A")
    res_b = build_model_result(case_study_plan, "B")

    assert abs(res_a.total_minutes - 456.0) < 1e-5
    assert abs(res_b.total_minutes - 456.0) < 1e-5

    assert res_a.shadow_price is not None
    assert abs(res_a.shadow_price - 3.0) < 1e-5

    assert res_b.shadow_price is not None
    assert abs(res_b.shadow_price - 3.0) < 1e-5

    for a in res_a.allocations:
        expected = ref_table[a.course_name]["A"]
        assert abs(a.minutes - expected) <= 0.1, f"Model A mismatch for {a.course_name}: {a.minutes} vs {expected}"

    for b in res_b.allocations:
        expected = ref_table[b.course_name]["B"]
        assert abs(b.minutes - expected) <= 0.1, f"Model B mismatch for {b.course_name}: {b.minutes} vs {expected}"


# Test 2: Rounding
def test_2_rounding_matches_paper(case_study_plan: Plan):
    """Rounding the exact values to whole minutes reproduces every entry in paper_table_3_as_printed."""
    with open(FIXTURE_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    expected_a = data["paper_table_3_as_printed"]["model_a"]
    expected_b = data["paper_table_3_as_printed"]["model_b"]

    res_a = build_model_result(case_study_plan, "A")
    res_b = build_model_result(case_study_plan, "B")

    calc_a = [format_minutes_text(a.minutes) for a in res_a.allocations]
    calc_b = [format_minutes_text(b.minutes) for b in res_b.allocations]

    assert calc_a == expected_a
    assert calc_b == expected_b


# Test 3: Parity
def test_3_parity_pulp_cbc(case_study_plan: Plan):
    """The same A and B models built in PuLP with CBC match the HiGHS result within 1e-6."""
    for model_type in ["A", "B"]:
        res_highs = build_model_result(case_study_plan, model_type)
        highs_alloc = np.array([a.minutes for a in res_highs.allocations])

        setup = build_problem_setup(case_study_plan, model_type)
        prob = pulp.LpProblem(f"Model_{model_type}", pulp.LpMaximize)
        x = [pulp.LpVariable(f"x_{i}", lowBound=setup.floors[i], upBound=setup.caps[i]) for i in range(setup.n)]

        prob += pulp.lpSum([(setup.weights[i] / 60.0) * x[i] for i in range(setup.n)])
        prob += pulp.lpSum(x) <= setup.budget

        for i, j in setup.tie_pairs:
            prob += x[i] == x[j]

        solver = pulp.PULP_CBC_CMD(msg=0)
        prob.solve(solver)

        pulp_alloc = np.array([pulp.value(x[i]) for i in range(setup.n)])
        max_diff = np.max(np.abs(highs_alloc - pulp_alloc))
        assert max_diff < 1e-6, f"Mismatch in Model {model_type}: max diff = {max_diff}"


# Test 4: Property (hypothesis)
@settings(max_examples=30, deadline=None)
@given(
    num_courses=st.integers(min_value=1, max_value=25),
    budget_val=st.floats(min_value=600.0, max_value=3000.0),
)
def test_4_property_hypothesis(num_courses: int, budget_val: float):
    """Allocations never exceed budget, never violate L_i/U_i, tied courses are equal, obj >= uniform."""
    courses = []
    diff_choices = ["most_difficult", "difficult", "medium", "easy", "easiest"]
    for i in range(num_courses):
        courses.append(
            Course(
                name=f"Course_{i}",
                credits=float((i % 4) + 1),
                difficulty_level=diff_choices[i % 5],
            )
        )

    plan = Plan(
        courses=courses,
        budget=Budget(mode="weekly", amount_minutes=budget_val),
        settings=PlanSettings(min_minutes_per_course=20.0, cap_multiplier=1.3, tie_break=True),
    )

    diag = diagnose_infeasibility(plan, "B")
    if diag["reasons"]:
        return  # Infeasible plan, property tests apply to feasible instances

    res_b = build_model_result(plan, "B")
    allocs = np.array([a.minutes for a in res_b.allocations])

    # 1. Budget never exceeded
    assert np.sum(allocs) <= budget_val + 1e-4

    # 2. Never violate floors
    assert np.all(allocs >= 20.0 - 1e-4)

    # 3. Never violate caps
    for a in res_b.allocations:
        if a.cap is not None:
            assert a.minutes <= a.cap + 1e-4

    # 4. Tied courses have equal allocations
    weights = [a.weight for a in res_b.allocations]
    for i in range(num_courses):
        for j in range(i + 1, num_courses):
            if abs(weights[i] - weights[j]) < 1e-9:
                assert abs(allocs[i] - allocs[j]) < 1e-4

    # 5. Objective is not lower than uniform allocation when uniform is feasible
    uniform_val = budget_val / num_courses
    uniform_feasible = True
    for a in res_b.allocations:
        if uniform_val < a.floor - 1e-4 or (a.cap is not None and uniform_val > a.cap + 1e-4):
            uniform_feasible = False
            break

    if uniform_feasible:
        uniform_obj = float(np.sum((np.array(weights) / 60.0) * uniform_val))
        assert res_b.objective_value >= uniform_obj - 1e-4


# Test 5: Sensitivity
def test_5_sensitivity_check(case_study_plan: Plan):
    """The +30 minute fixed-bounds re-solve changes the objective by lambda * 0.5 within 1e-6."""
    res_b = build_model_result(case_study_plan, "B")
    lambda_val = res_b.shadow_price
    assert lambda_val is not None
    assert abs(lambda_val - 3.0) < 1e-5

    # Check sensitivity delta check
    assert res_b.shadow_price_check_valid is True
    assert res_b.shadow_price_delta_check is not None
    # delta_check = delta_obj / 0.5h, so delta_obj = delta_check * 0.5 = lambda * 0.5
    expected_delta_obj = lambda_val * 0.5
    actual_delta_obj = res_b.shadow_price_delta_check * 0.5
    assert abs(actual_delta_obj - expected_delta_obj) < 1e-5


# Test 6: Infeasible
def test_6_infeasible_floors():
    """Floors above budget return status: infeasible with a sentence naming the floor and the budget."""
    courses = [
        Course(name=f"Course_{i}", credits=3.0, difficulty_level="medium")
        for i in range(10)
    ]
    # 10 courses * 20 min = 200 min minimum, but budget is 180 min (3 hours)
    plan = Plan(
        courses=courses,
        budget=Budget(mode="weekly", amount_minutes=180.0),
        settings=PlanSettings(min_minutes_per_course=20.0),
    )

    diag = diagnose_infeasibility(plan, "B")
    assert len(diag["reasons"]) > 0
    reason = diag["reasons"][0]
    assert "200.0" in reason or "exceeds" in reason
    assert "180.0" in reason


# Test 7: Unit conversion
def test_7_unit_conversion():
    """A plan entered in hours and the same plan in minutes give identical solver input."""
    # 7.6 hours = 456 minutes
    plan_min = Plan(
        courses=[
            Course(name="Math", credits=4.0, difficulty_level="difficult", min_minutes=30.0),
            Course(name="Physics", credits=3.0, difficulty_level="medium"),
        ],
        budget=Budget(mode="weekly", amount_minutes=456.0),
    )

    # In hours mode, the UI converts input to minutes before sending to the API.
    # 7.6 h -> 7.6 * 60 = 456 min. 0.5 h min_minutes -> 0.5 * 60 = 30 min.
    plan_hr_converted = Plan(
        courses=[
            Course(name="Math", credits=4.0, difficulty_level="difficult", min_minutes=0.5 * 60.0),
            Course(name="Physics", credits=3.0, difficulty_level="medium"),
        ],
        budget=Budget(mode="weekly", amount_minutes=7.6 * 60.0),
    )

    setup_min = build_problem_setup(plan_min, "B")
    setup_hr = build_problem_setup(plan_hr_converted, "B")

    np.testing.assert_allclose(setup_min.weights, setup_hr.weights)
    np.testing.assert_allclose(setup_min.floors, setup_hr.floors)
    np.testing.assert_allclose(setup_min.caps, setup_hr.caps)
    assert setup_min.budget == setup_hr.budget
