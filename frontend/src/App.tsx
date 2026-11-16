import React, { useEffect, useRef, useState } from "react";
import { Masthead } from "./components/Masthead";
import { Intro } from "./components/Intro";
import { StageA_Plan } from "./components/Calculator/StageA_Plan";
import { StageB_Rules } from "./components/Calculator/StageB_Rules";
import { StageC_Results } from "./components/Calculator/StageC_Results";
import { Method } from "./components/Method";
import { CaseStudyDrawer } from "./components/CaseStudyDrawer";
import { About } from "./components/About";
import { Footer } from "./components/Footer";
import type { BudgetMode, Course, Period, Plan, PlanSettings, Rule, SolveResponse } from "./types";
import { fetchCaseStudy, fetchHealth, solvePlan } from "./api";
import { getStrings, type Lang } from "./content/strings";

const DEFAULT_SETTINGS: PlanSettings = {
  min_minutes_per_course: 20.0,
  tie_break: true,
  treat_unassigned_as_easiest: false,
  diminishing_lengths: [60.0, 60.0],
  diminishing_factors: [1.0, 0.6, 0.3],
  diminishing_cap_enabled: false,
  difficulty_multipliers: { most_difficult: 1.2, difficult: 1.1, medium: 1.0, easy: 0.9, easiest: 0.8 },
};

const DEFAULT_COURSES: Course[] = [
  { id: "c1", name: "Calculus", credits: 4.0, difficulty_level: "difficult", min_minutes: null, max_minutes: null, locked_minutes: null },
  { id: "c2", name: "Linear Algebra", credits: 3.0, difficulty_level: "medium", min_minutes: null, max_minutes: null, locked_minutes: null },
  { id: "c3", name: "Mechanics", credits: 4.0, difficulty_level: "most_difficult", min_minutes: null, max_minutes: null, locked_minutes: null },
];

const ensureIds = (courses: Course[]) => courses.map((c, i) => ({ ...c, id: c.id || `c_${i}_${Date.now()}_${Math.random().toString(36).slice(2, 6)}` }));

export const App: React.FC = () => {
  const [lang, setLang] = useState<Lang>(() => (localStorage.getItem("study_budget_lang") as Lang) || "en");
  const [theme, setTheme] = useState<"light" | "dark">(() => (localStorage.getItem("study_budget_theme") as "light" | "dark") || "light");
  const t = getStrings(lang);

  const [courses, setCourses] = useState<Course[]>(() => {
    const saved = localStorage.getItem("study_budget_courses");
    return ensureIds(saved ? JSON.parse(saved) : DEFAULT_COURSES);
  });
  const [budgetMode, setBudgetMode] = useState<BudgetMode>(() => (localStorage.getItem("study_budget_mode") as BudgetMode) || "weekly");
  const [budgetAmount, setBudgetAmount] = useState<number>(() => { const s = localStorage.getItem("study_budget_amount"); return s ? parseFloat(s) : 450; });
  const [daysPerWeek, setDaysPerWeek] = useState<number>(() => { const s = localStorage.getItem("study_budget_days"); return s ? parseInt(s, 10) : 5; });
  const [customPeriods, setCustomPeriods] = useState<Period[]>(() => {
    const s = localStorage.getItem("study_budget_periods");
    return s ? JSON.parse(s) : [
      { label: "Monday", minutes: 90 }, { label: "Tuesday", minutes: 90 }, { label: "Wednesday", minutes: 90 }, { label: "Thursday", minutes: 90 }, { label: "Friday", minutes: 90 },
    ];
  });
  const [rules, setRules] = useState<Rule[]>(() => { const s = localStorage.getItem("study_budget_rules"); return s ? JSON.parse(s) : []; });
  const [settings, setSettings] = useState<PlanSettings>(() => {
    const s = localStorage.getItem("study_budget_settings");
    const parsed = s ? JSON.parse(s) : {};
    return { ...DEFAULT_SETTINGS, ...parsed, difficulty_multipliers: { ...DEFAULT_SETTINGS.difficulty_multipliers, ...(parsed.difficulty_multipliers || {}) } };
  });
  const [unit, setUnit] = useState<"min" | "h">(() => (localStorage.getItem("study_budget_unit") as "min" | "h") || "min");

  const [solveResponse, setSolveResponse] = useState<SolveResponse | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const [isOutOfDate, setIsOutOfDate] = useState(false);
  const [isCaseStudyLoaded, setIsCaseStudyLoaded] = useState(false);
  const [caseStudyData, setCaseStudyData] = useState<any>(null);
  const [showGridOverlay, setShowGridOverlay] = useState(false);
  const [backendStatus, setBackendStatus] = useState<"ok" | "starting" | "offline">("starting");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const calculatorRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => { localStorage.setItem("study_budget_lang", lang); document.documentElement.lang = lang === "bn" ? "bn" : "en"; }, [lang]);
  useEffect(() => { localStorage.setItem("study_budget_theme", theme); document.documentElement.setAttribute("data-theme", theme); }, [theme]);

  useEffect(() => {
    localStorage.setItem("study_budget_courses", JSON.stringify(courses));
    localStorage.setItem("study_budget_mode", budgetMode);
    localStorage.setItem("study_budget_amount", String(budgetAmount));
    localStorage.setItem("study_budget_days", String(daysPerWeek));
    localStorage.setItem("study_budget_periods", JSON.stringify(customPeriods));
    localStorage.setItem("study_budget_rules", JSON.stringify(rules));
    localStorage.setItem("study_budget_settings", JSON.stringify(settings));
    localStorage.setItem("study_budget_unit", unit);
    if (solveResponse) setIsOutOfDate(true);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [courses, budgetMode, budgetAmount, daysPerWeek, customPeriods, rules, settings, unit]);

  useEffect(() => {
    let cancelled = false;
    const check = async () => {
      const res = await fetchHealth();
      if (cancelled) return;
      setBackendStatus((prev) => (res.status === "ok" ? "ok" : prev === "starting" ? "starting" : "offline"));
    };
    check();
    const id = window.setInterval(check, 2500);
    const timeout = window.setTimeout(() => { if (!cancelled) setBackendStatus((p) => (p === "starting" ? "offline" : p)); }, 15000);
    fetchCaseStudy().then((data) => { if (!cancelled) setCaseStudyData(data); }).catch(() => {});
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.key === "g" || e.key === "G") && !["INPUT", "TEXTAREA", "SELECT"].includes((e.target as HTMLElement).tagName)) setShowGridOverlay((v) => !v);
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => { cancelled = true; window.clearInterval(id); window.clearTimeout(timeout); window.removeEventListener("keydown", handleKeyDown); };
  }, []);

  const buildCurrentPlan = (): Plan => {
    // derive table constraint rules from course rows so solver sees them; keep user-added non-table rules
    const tableRules: Rule[] = [];
    for (const c of courses) {
      const cid = c.name;
      if (c.locked_minutes != null && !Number.isNaN(c.locked_minutes)) {
        tableRules.push({ id: `tbl-lock-${c.id || cid}`, type: "lock", enabled: true, course_id: cid, time_minutes: c.locked_minutes });
      } else {
        if (c.min_minutes != null && !Number.isNaN(c.min_minutes)) tableRules.push({ id: `tbl-min-${c.id || cid}`, type: "min", enabled: true, course_id: cid, time_minutes: c.min_minutes });
        if (c.max_minutes != null && !Number.isNaN(c.max_minutes)) tableRules.push({ id: `tbl-max-${c.id || cid}`, type: "max", enabled: true, course_id: cid, time_minutes: c.max_minutes });
      }
    }
    const userRules = rules.filter((r) => !String(r.id || "").startsWith("tbl-"));
    return {
      courses: courses.map((c) => ({ ...c, id: c.name })), // use name as stable id for backend matching
      budget: {
        mode: budgetMode,
        amount_minutes: budgetAmount,
        days_per_week: budgetMode === "daily" ? daysPerWeek : undefined,
        periods: budgetMode === "custom" ? customPeriods : undefined,
      },
      rules: [...userRules, ...tableRules],
      settings,
    };
  };

  const handleRunModels = async () => {
    if (courses.length === 0) return;
    setIsRunning(true);
    setErrorMessage(null);
    try {
      const resp = await solvePlan(buildCurrentPlan(), ["A", "B", "C"]);
      setSolveResponse(resp);
      setIsOutOfDate(false);
      if (resp.status === "error") setErrorMessage(resp.reasons?.[0] || t.errors.parseFailed);
    } catch (err: any) {
      const msg = err?.message || "Failed to solve models.";
      setErrorMessage(msg);
      setSolveResponse({ status: "error", results: {}, explanations: [], reasons: [msg], suggestions: [] });
    } finally {
      setIsRunning(false);
    }
  };

  const handleLoadCaseStudy = async () => {
    setIsRunning(true);
    setErrorMessage(null);
    try {
      const data = caseStudyData || await fetchCaseStudy();
      if (!caseStudyData) setCaseStudyData(data);
      const loadedCourses: Course[] = (data.courses || []).map((c: any, i: number) => ({
        id: `cs_${i}`, name: c.name, credits: c.credits, difficulty_level: c.difficulty_level ?? null, min_minutes: null, max_minutes: null, locked_minutes: null,
      }));
      const nextSettings: PlanSettings = {
        ...DEFAULT_SETTINGS,
        min_minutes_per_course: data.settings?.min_minutes ?? DEFAULT_SETTINGS.min_minutes_per_course,
        tie_break: data.settings?.tie_break ?? DEFAULT_SETTINGS.tie_break,
      };
      setCourses(loadedCourses);
      setBudgetMode(data.budget?.mode || "weekly");
      setBudgetAmount(data.budget?.amount_minutes ?? 456);
      setDaysPerWeek(data.budget?.days_per_week ?? 5);
      setCustomPeriods(data.budget?.periods ?? customPeriods);
      setSettings(nextSettings);
      setRules([]);
      setIsCaseStudyLoaded(true);
      const plan: Plan = { courses: loadedCourses.map(c => ({ ...c, id: c.name })), budget: { mode: data.budget?.mode || "weekly", amount_minutes: data.budget?.amount_minutes ?? 456, days_per_week: data.budget?.days_per_week, periods: data.budget?.periods }, rules: [], settings: nextSettings };
      const resp = await solvePlan(plan, ["A", "B", "C"]);
      setSolveResponse(resp);
      setIsOutOfDate(false);
      if (resp.status === "error") setErrorMessage(resp.reasons?.[0] || "Failed to solve case study.");
      calculatorRef.current?.scrollIntoView({ behavior: "smooth" });
    } catch (err: any) {
      const msg = err?.message || "Failed to load case study.";
      setErrorMessage(msg);
      setSolveResponse({ status: "error", results: {}, explanations: [], reasons: [msg], suggestions: [] });
    } finally {
      setIsRunning(false);
    }
  };

  const handleClearCaseStudy = () => {
    setCourses([]);
    setRules([]);
    setSolveResponse(null);
    setIsCaseStudyLoaded(false);
    setErrorMessage(null);
  };

  return (
    <div className="page-container">
      {showGridOverlay && <div className="grid-overlay" aria-hidden="true">{Array.from({ length: 12 }).map((_, i) => <div key={i} className="grid-col-line" />)}</div>}
      <Masthead lang={lang} onLangChange={setLang} theme={theme} onThemeChange={setTheme} t={t} />
      <Intro onLoadCaseStudy={handleLoadCaseStudy} t={t} />
      <section id="calculator" ref={calculatorRef} className="section-block">
        <div className="section-rule" />
        <div className="section-header-row">
          <span className="font-label" style={{ color: "var(--ink-3)" }}>{t.calculator.sectionNumber}</span>
          <h2 className="font-h1">{t.calculator.sectionTitle}</h2>
        </div>
        {isCaseStudyLoaded && (
          <div className="banner">
            <span className="font-small" style={{ fontWeight: 500 }}>{t.calculator.caseStudyBanner}</span>
            <button type="button" onClick={handleClearCaseStudy} className="link-button">{t.calculator.clearCaseStudy}</button>
          </div>
        )}
        {backendStatus === "starting" && <div className="notice font-small">{t.calculator.solverAsleepNotice}</div>}
        {backendStatus === "offline" && <div className="notice notice-warn font-small">{t.calculator.offlineNotice}</div>}
        {errorMessage && <div className="notice notice-warn font-small">{errorMessage}</div>}
        <StageA_Plan courses={courses} onCoursesChange={setCourses} budgetMode={budgetMode} onBudgetModeChange={setBudgetMode} budgetAmount={budgetAmount} onBudgetAmountChange={setBudgetAmount} daysPerWeek={daysPerWeek} onDaysPerWeekChange={setDaysPerWeek} customPeriods={customPeriods} onCustomPeriodsChange={setCustomPeriods} settings={settings} onSettingsChange={setSettings} unit={unit} onUnitChange={setUnit} t={t} lang={lang} />
        <StageB_Rules rules={rules} onRulesChange={setRules} courses={courses} unit={unit} t={t} />
        <StageC_Results solveResponse={solveResponse} isRunning={isRunning} onRunModels={handleRunModels} isOutOfDate={isOutOfDate} unit={unit} minFloorMinutes={settings.min_minutes_per_course} planPayload={buildCurrentPlan()} t={t} />
      </section>
      <Method t={t} />
      <CaseStudyDrawer onLoadCaseStudy={handleLoadCaseStudy} caseStudyData={caseStudyData} t={t} />
      <About t={t} />
      <Footer t={t} />
    </div>
  );
};

export default App;
