export type DifficultyLevel = "most_difficult" | "difficult" | "medium" | "easy" | "easiest";
export type BudgetMode = "weekly" | "daily" | "custom";
export type RuleType = "min" | "max" | "lock" | "boost" | "dependency" | "group_limit" | "unavailable";
export type ModelType = "A" | "B" | "C";
export type TimeUnit = "min" | "h";

export interface DifficultyMultipliers {
  most_difficult: number;
  difficult: number;
  medium: number;
  easy: number;
  easiest: number;
}

export interface Course {
  id?: string;
  name: string;
  credits: number;
  difficulty_level: DifficultyLevel | null;
  custom_difficulty?: number | null;
  min_minutes?: number | null;
  max_minutes?: number | null;
  locked_minutes?: number | null;
}

export interface Period {
  label: string;
  minutes: number;
}

export interface Budget {
  mode: BudgetMode;
  amount_minutes?: number;
  days_per_week?: number;
  periods?: Period[];
}

export interface Rule {
  id: string;
  type: RuleType;
  enabled: boolean;
  course_id?: string;
  target_course_id?: string;
  group_course_ids?: string[];
  time_minutes?: number;
  boost_factor?: number;
  dependency_k?: number;
  period_label?: string;
}

export interface PlanSettings {
  min_minutes_per_course: number;
  tie_break: boolean;
  treat_unassigned_as_easiest: boolean;
  diminishing_lengths: number[];
  diminishing_factors: number[];
  diminishing_cap_enabled: boolean;
  difficulty_multipliers?: DifficultyMultipliers;
}

export interface Plan {
  courses: Course[];
  budget: Budget;
  rules: Rule[];
  settings: PlanSettings;
}

export interface CourseAllocation {
  course_name: string;
  minutes: number;
  weight: number;
  cap?: number | null;
  floor: number;
  status: "at_minimum" | "at_cap" | "at_user_maximum" | "locked" | "free";
  is_min_allocation: boolean;
  is_max_allocation: boolean;
}

export interface ConstraintStatus {
  name: string;
  description: string;
  slack_minutes: number;
  is_binding: boolean;
}

export interface ModelResult {
  model: ModelType;
  allocations: CourseAllocation[];
  total_minutes: number;
  objective_value: number;
  solver_status: string;
  wall_time_ms: number;
  shadow_price?: number;
  shadow_price_delta_check?: number;
  shadow_price_check_valid: boolean;
  next_hour_courses: string[];
  constraints: ConstraintStatus[];
  tie_breaks_skipped: string[];
}

export interface PeriodSchedule {
  period_label: string;
  budget_minutes: number;
  allocations: Record<string, number>;
}

export interface SolveResponse {
  status: "optimal" | "infeasible" | "error";
  results: Record<string, ModelResult>;
  explanations: string[];
  reasons: string[];
  suggestions: string[];
  schedule?: PeriodSchedule[] | null;
}

export interface ParsedCourse {
  name: string;
  credits?: number | null;
  weight_basis?: "credits" | "marks" | "other" | null;
  difficulty_level?: DifficultyLevel | null;
  min_minutes?: number | null;
  max_minutes?: number | null;
  locked_minutes?: number | null;
  source_quote?: string;
  confidence?: "high" | "medium" | "low";
}

export interface ParsedPlan {
  courses: ParsedCourse[];
  budget?: {
    mode?: BudgetMode;
    amount_minutes?: number;
    days_per_week?: number;
    periods?: Period[];
    source_quote?: string;
  };
  rules: Array<{
    type: RuleType;
    fields: Record<string, any>;
    source_quote?: string;
    confidence?: "high" | "medium" | "low";
  }>;
  warnings: string[];
  questions: string[];
}
