"""Pydantic schemas for the study optimizer."""
from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field, field_validator, model_validator

DifficultyLevel = Literal["most_difficult", "difficult", "medium", "easy", "easiest"]
BudgetMode = Literal["weekly", "daily", "custom"]
RuleType = Literal["min", "max", "lock", "boost", "dependency", "group_limit", "unavailable"]
ModelType = Literal["A", "B", "C"]
AllocationStatus = Literal["at_minimum", "at_cap", "at_user_maximum", "locked", "free"]

DIFFICULTY_COEFFICIENTS: Dict[DifficultyLevel, float] = {
    "most_difficult": 1.2,
    "difficult": 1.1,
    "medium": 1.0,
    "easy": 0.9,
    "easiest": 0.8,
}


class Course(BaseModel):
    id: Optional[str] = None
    name: str = Field(..., min_length=1, max_length=120)
    credits: float = Field(..., gt=0, le=1000)
    difficulty_level: Optional[DifficultyLevel] = None
    custom_difficulty: Optional[float] = Field(None, ge=0.5, le=2.0)
    min_minutes: Optional[float] = Field(None, ge=0)
    max_minutes: Optional[float] = Field(None, ge=0)
    locked_minutes: Optional[float] = Field(None, ge=0)

    @model_validator(mode="after")
    def check_bounds(self) -> "Course":
        if self.min_minutes is not None and self.max_minutes is not None:
            if self.min_minutes > self.max_minutes:
                raise ValueError(
                    f"Minimum minutes ({self.min_minutes}) cannot exceed maximum minutes ({self.max_minutes}) for course '{self.name}'."
                )
        return self


class Period(BaseModel):
    label: str = Field(..., min_length=1, max_length=120)
    minutes: float = Field(..., ge=0)


class Budget(BaseModel):
    mode: BudgetMode
    amount_minutes: Optional[float] = Field(None, gt=0)
    days_per_week: Optional[int] = Field(None, ge=1, le=7)
    periods: Optional[List[Period]] = None

    @property
    def total_minutes(self) -> float:
        if self.mode == "weekly":
            if self.amount_minutes is None:
                raise ValueError("Weekly budget requires amount_minutes.")
            return float(self.amount_minutes)
        elif self.mode == "daily":
            if self.amount_minutes is None:
                raise ValueError("Daily budget requires amount_minutes.")
            days = self.days_per_week if self.days_per_week is not None else 7
            return float(self.amount_minutes * days)
        elif self.mode == "custom":
            if not self.periods:
                raise ValueError("Custom budget requires a non-empty list of periods.")
            return float(sum(p.minutes for p in self.periods))
        raise ValueError(f"Unknown budget mode: {self.mode}")


class Rule(BaseModel):
    id: Optional[str] = None
    type: RuleType
    enabled: bool = True
    course_id: Optional[str] = None  # course id or exact course name
    target_course_id: Optional[str] = None  # course id or name for dependency x_A >= k * x_B
    group_course_ids: Optional[List[str]] = None
    time_minutes: Optional[float] = Field(None, ge=0)
    boost_factor: Optional[float] = Field(None, gt=0, le=10.0)
    dependency_k: Optional[float] = Field(None, gt=0, le=100.0)
    period_label: Optional[str] = None


class PlanSettings(BaseModel):
    min_minutes_per_course: float = Field(20.0, ge=0)
    tie_break: bool = True
    treat_unassigned_as_easiest: bool = False
    diminishing_lengths: List[float] = [60.0, 60.0]  # K=3: lengths (60, 60, inf)
    diminishing_factors: List[float] = [1.0, 0.6, 0.3]  # phi
    diminishing_cap_enabled: bool = False
    difficulty_multipliers: Dict[str, float] = Field(
        default_factory=lambda: {
            "most_difficult": 1.2,
            "difficult": 1.1,
            "medium": 1.0,
            "easy": 0.9,
            "easiest": 0.8,
        }
    )


class Plan(BaseModel):
    courses: List[Course] = Field(..., min_length=1, max_length=200)
    budget: Budget
    rules: List[Rule] = Field(default_factory=list, max_length=100)
    settings: PlanSettings = Field(default_factory=PlanSettings)

    @field_validator("courses")
    @classmethod
    def check_duplicate_names(cls, v: List[Course]) -> List[Course]:
        names = [c.name.strip().lower() for c in v]
        if len(names) != len(set(names)):
            raise ValueError("Course names must be unique.")
        return v


class SolveRequest(BaseModel):
    plan: Plan
    models: List[ModelType] = ["A", "B", "C"]


class CourseAllocation(BaseModel):
    course_name: str
    minutes: float
    weight: float
    cap: Optional[float] = None
    floor: float
    status: AllocationStatus
    is_min_allocation: bool = False
    is_max_allocation: bool = False


class ConstraintStatus(BaseModel):
    name: str
    description: str
    slack_minutes: float
    is_binding: bool


class ModelResult(BaseModel):
    model: ModelType
    allocations: List[CourseAllocation]
    total_minutes: float
    objective_value: float
    solver_status: str
    wall_time_ms: float
    shadow_price: Optional[float] = None  # dual marginal * 60 (units per hour)
    shadow_price_delta_check: Optional[float] = None  # Delta objective / 0.5h
    shadow_price_check_valid: bool = True
    next_hour_courses: List[str] = []
    constraints: List[ConstraintStatus] = []
    tie_breaks_skipped: List[str] = []


class PeriodSchedule(BaseModel):
    period_label: str
    budget_minutes: float
    allocations: Dict[str, float]  # course_name -> minutes


class SolveResponse(BaseModel):
    status: Literal["optimal", "infeasible", "error"]
    results: Dict[str, ModelResult] = {}
    explanations: List[str] = []
    reasons: List[str] = []
    suggestions: List[str] = []
    schedule: Optional[List[PeriodSchedule]] = None


# Multimodal parser schemas
class ParsedCourse(BaseModel):
    name: str
    credits: Optional[float] = None
    weight_basis: Optional[Literal["credits", "marks", "other"]] = None
    difficulty_level: Optional[DifficultyLevel] = None
    min_minutes: Optional[float] = None
    max_minutes: Optional[float] = None
    locked_minutes: Optional[float] = None
    source_quote: str = ""
    confidence: Literal["high", "medium", "low"] = "medium"


class ParsedBudget(BaseModel):
    mode: Optional[BudgetMode] = None
    amount_minutes: Optional[float] = None
    days_per_week: Optional[int] = None
    periods: List[Period] = []
    source_quote: str = ""


class ParsedRule(BaseModel):
    type: RuleType
    fields: Dict[str, Any] = {}
    source_quote: str = ""
    confidence: Literal["high", "medium", "low"] = "medium"


class ParsedPlan(BaseModel):
    courses: List[ParsedCourse] = []
    budget: Optional[ParsedBudget] = None
    rules: List[ParsedRule] = []
    warnings: List[str] = []
    questions: List[str] = []
