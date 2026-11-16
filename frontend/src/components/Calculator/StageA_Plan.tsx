import React, { useRef, useState } from "react";
import type { BudgetMode, Course, DifficultyLevel, Period, PlanSettings, TimeUnit } from "../../types";
import type { Strings, Lang } from "../../content/strings";
import { parseMultimodal } from "../../api";

interface StageAPlanProps {
  courses: Course[];
  onCoursesChange: (courses: Course[]) => void;
  budgetMode: BudgetMode;
  onBudgetModeChange: (mode: BudgetMode) => void;
  budgetAmount: number;
  onBudgetAmountChange: (amount: number) => void;
  daysPerWeek: number;
  onDaysPerWeekChange: (days: number) => void;
  customPeriods: Period[];
  onCustomPeriodsChange: (periods: Period[]) => void;
  settings: PlanSettings;
  onSettingsChange: (settings: PlanSettings) => void;
  unit: TimeUnit;
  onUnitChange: (unit: TimeUnit) => void;
  t: Strings;
  lang: Lang;
}

const DIFF_KEYS: DifficultyLevel[] = ["most_difficult", "difficult", "medium", "easy", "easiest"];

export const StageA_Plan: React.FC<StageAPlanProps> = (props) => {
  const { courses, onCoursesChange, budgetMode, onBudgetModeChange, budgetAmount, onBudgetAmountChange, daysPerWeek, onDaysPerWeekChange, customPeriods, onCustomPeriodsChange, settings, onSettingsChange, unit, onUnitChange, t } = props;
  const ta = t.stageA;
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [parseText, setParseText] = useState("");
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [isParsing, setIsParsing] = useState(false);
  const [parseError, setParseError] = useState<string | null>(null);
  const [parseQuestions, setParseQuestions] = useState<string[]>([]);
  const [isRecording, setIsRecording] = useState(false);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const nameInputRefs = useRef<Record<string, HTMLInputElement | null>>({});

  const toDisplay = (minutes: number | null | undefined): string => {
    if (minutes == null || Number.isNaN(minutes)) return "";
    return unit === "min" ? String(Math.round(minutes * 100) / 100) : String(Math.round((minutes / 60) * 1000) / 1000);
  };
  const fromDisplay = (val: string): number | null => {
    if (val === "" || val == null) return null;
    const num = parseFloat(val);
    if (Number.isNaN(num)) return null;
    return unit === "min" ? num : num * 60;
  };

  const multipliers = settings.difficulty_multipliers || { most_difficult: 1.2, difficult: 1.1, medium: 1.0, easy: 0.9, easiest: 0.8 };

  const handleAddCourse = (focusId?: string) => {
    const id = `c_${Date.now()}_${Math.random().toString(36).slice(2, 7)}`;
    const newCourse: Course = { id, name: "", credits: 3.0, difficulty_level: null, min_minutes: null, max_minutes: null, locked_minutes: null };
    onCoursesChange([...courses, newCourse]);
    if (focusId) {
      setTimeout(() => nameInputRefs.current[id]?.focus(), 0);
    }
    return id;
  };

  const handleUpdateCourse = (index: number, updates: Partial<Course>) => {
    const updated = [...courses];
    const cur = { ...updated[index], ...updates };
    // enforce lock exclusivity: if lock set, clear/disable min/max
    if (Object.prototype.hasOwnProperty.call(updates, "locked_minutes")) {
      if (cur.locked_minutes != null && !Number.isNaN(cur.locked_minutes as any)) {
        cur.min_minutes = null;
        cur.max_minutes = null;
      }
    }
    updated[index] = cur;
    onCoursesChange(updated);
  };

  const handleRemoveCourse = (index: number) => onCoursesChange(courses.filter((_, i) => i !== index));

  const handleNameKeyDown = (e: React.KeyboardEvent<HTMLInputElement>, index: number) => {
    if (e.key === "Enter") {
      e.preventDefault();
      const id = `c_${Date.now()}_${Math.random().toString(36).slice(2, 7)}`;
      const newCourse: Course = { id, name: "", credits: 3.0, difficulty_level: null, min_minutes: null, max_minutes: null, locked_minutes: null };
      const updated = [...courses.slice(0, index + 1), newCourse, ...courses.slice(index + 1)];
      onCoursesChange(updated);
      setTimeout(() => nameInputRefs.current[id]?.focus(), 0);
    }
  };

  const handlePasteSpreadsheet = (e: React.ClipboardEvent<HTMLInputElement>, index: number) => {
    const clipData = e.clipboardData.getData("text");
    if (!clipData || !clipData.includes("\t")) return;
    e.preventDefault();
    const rows = clipData.trim().split(/\r\n|\n|\r/);
    const parsedCourses: Course[] = [];
    for (const r of rows) {
      const cols = r.split("\t");
      if (!cols[0]) continue;
      const name = cols[0].trim();
      const credits = parseFloat(cols[1]) || 3.0;
      let diff: DifficultyLevel | null = null;
      if (cols[2]) {
        const dStr = cols[2].toLowerCase().replace(/\s+/g, "_");
        if ((DIFF_KEYS as string[]).includes(dStr)) diff = dStr as DifficultyLevel;
      }
      parsedCourses.push({ id: `p_${Date.now()}_${Math.random().toString(36).slice(2,6)}`, name, credits, difficulty_level: diff, min_minutes: null, max_minutes: null, locked_minutes: null });
    }
    if (parsedCourses.length > 0) {
      const updated = [...courses.slice(0, index), ...parsedCourses, ...courses.slice(index + 1)];
      onCoursesChange(updated);
    }
  };

  const handleRunParser = async () => {
    if (!parseText.trim() && selectedFiles.length === 0) return;
    setIsParsing(true); setParseError(null); setParseQuestions([]);
    try {
      const parsed = await parseMultimodal(parseText, selectedFiles);
      if (parsed.courses && parsed.courses.length > 0) {
        onCoursesChange(parsed.courses.map((pc, i) => ({
          id: `pc_${Date.now()}_${i}`, name: pc.name, credits: pc.credits || 3.0, difficulty_level: pc.difficulty_level || null,
          min_minutes: pc.min_minutes ?? null, max_minutes: pc.max_minutes ?? null, locked_minutes: pc.locked_minutes ?? null,
        })));
      }
      if (parsed.budget?.amount_minutes) {
        onBudgetAmountChange(parsed.budget.amount_minutes);
        if (parsed.budget.mode) onBudgetModeChange(parsed.budget.mode);
        if (parsed.budget.days_per_week) onDaysPerWeekChange(parsed.budget.days_per_week);
      }
      if (parsed.questions?.length) setParseQuestions(parsed.questions);
      setParseText(""); setSelectedFiles([]);
    } catch (err: any) {
      setParseError(err.message || t.errors.parseFailed);
    } finally { setIsParsing(false); }
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream, { mimeType: "audio/webm" });
      mediaRecorderRef.current = recorder; audioChunksRef.current = [];
      recorder.ondataavailable = (e) => { if (e.data.size > 0) audioChunksRef.current.push(e.data); };
      recorder.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: "audio/webm" });
        const audioFile = new File([audioBlob], "voice-input.webm", { type: "audio/webm" });
        setSelectedFiles((prev) => [...prev, audioFile]);
        stream.getTracks().forEach((track) => track.stop());
      };
      recorder.start(); setIsRecording(true);
    } catch { setParseError("Microphone access was denied or not supported."); }
  };
  const stopRecording = () => { if (mediaRecorderRef.current && isRecording) { mediaRecorderRef.current.stop(); setIsRecording(false); } };

  const updateMultiplier = (key: DifficultyLevel, value: number) => {
    onSettingsChange({ ...settings, difficulty_multipliers: { ...multipliers, [key]: value } });
  };

  return (
    <div style={{ marginBottom: "40px" }}>
      <div style={{ display: "flex", alignItems: "baseline", gap: "16px", marginBottom: "20px", flexWrap: "wrap" }}>
        <span className="font-label" style={{ color: "var(--ink-3)" }}>{ta.stepNumber}</span>
        <h3 className="font-h3">{ta.title}</h3>
        <span className="font-small" style={{ color: "var(--ink-2)" }}>{ta.subtitle}</span>
      </div>

      <div style={{ border: "1px solid var(--rule)", backgroundColor: "var(--paper-2)", padding: "20px", marginBottom: "24px" }}>
        <div style={{ marginBottom: "10px", display: "flex", justifyContent: "space-between", alignItems: "baseline", gap: "12px", flexWrap: "wrap" }}>
          <label className="font-label">{ta.parserLabel}</label>
          <span className="font-small" style={{ color: "var(--ink-3)" }}>{ta.parserHelp}</span>
        </div>
        <div style={{ display: "flex", gap: "12px", flexDirection: "column" }}>
          <textarea aria-label="Paste syllabus or timetable text" value={parseText} onChange={(e) => setParseText(e.target.value)} placeholder="Paste syllabus notes, course lists, or timetable text..." style={{ width: "100%", minHeight: "72px", padding: "10px", border: "1px solid var(--rule-soft)", background: "var(--paper)", fontFamily: "var(--font-sans)", fontSize: "14px", resize: "vertical" }} />
          <div style={{ display: "flex", gap: "10px", alignItems: "center", flexWrap: "wrap" }}>
            <input type="file" multiple accept="image/*,.pdf,.docx,audio/*" onChange={(e) => { if (e.target.files) setSelectedFiles(Array.from(e.target.files)); }} style={{ display: "none" }} id="file-upload-input" />
            <label htmlFor="file-upload-input" style={{ height: "36px", padding: "0 14px", border: "1px solid var(--ink)", background: "var(--paper)", cursor: "pointer", display: "inline-flex", alignItems: "center" }} className="font-label">Attach ({selectedFiles.length})</label>
            {!isRecording ? <button type="button" onClick={startRecording} style={{ height: "36px" }}>{ta.parserButtons.record}</button> : <button type="button" onClick={stopRecording} style={{ height: "36px", background: "var(--accent)", color: "#fff" }}>{ta.parserButtons.stop}</button>}
            <button type="button" className="primary" onClick={handleRunParser} disabled={isParsing || (!parseText.trim() && selectedFiles.length === 0)} style={{ height: "36px" }}>{isParsing ? t.calculator.loadingNotice : ta.parserButtons.readThis}</button>
          </div>
          {parseError && <div style={{ color: "var(--warn)" }} className="font-small">! {parseError}</div>}
          {parseQuestions.length > 0 && <div style={{ padding: "10px", border: "1px solid var(--rule-soft)", background: "var(--paper)" }}><span className="font-label">Questions</span><ul style={{ paddingLeft: "20px", marginTop: "6px" }}>{parseQuestions.map((q, i) => <li key={i} className="font-small">{q}</li>)}</ul></div>}
        </div>
      </div>

      {courses.length > 30 && <div style={{ marginBottom: "12px", padding: "8px 12px", border: "1px solid var(--rule-soft)", color: "var(--ink-2)" }} className="font-small">{ta.courseCountWarning}</div>}

      {courses.length === 0 ? (
        <div style={{ padding: "28px", border: "1px dashed var(--rule-soft)", textAlign: "center" }} className="font-body">{ta.emptyState}</div>
      ) : (
        <div className="table-wrap">
          <table className="data-table">
            <thead>
              <tr>
                <th className="font-label" style={{ minWidth: "180px" }}>{ta.tableHeaders.course}</th>
                <th className="font-label" style={{ width: "90px" }}>{ta.tableHeaders.credits}</th>
                {DIFF_KEYS.map((k) => (
                  <th key={k} className="font-label" style={{ textAlign: "center", minWidth: "110px" }}>
                    <div>{ta.difficultyLabels[k].label}</div>
                    <div style={{ fontWeight: 500, color: "var(--ink-2)", marginTop: "2px" }}>{multipliers[k].toFixed(2)}</div>
                  </th>
                ))}
                <th className="font-label" style={{ width: "90px" }}>{ta.tableHeaders.min} ({unit})</th>
                <th className="font-label" style={{ width: "90px" }}>{ta.tableHeaders.max} ({unit})</th>
                <th className="font-label" style={{ width: "90px" }}>{ta.tableHeaders.lock} ({unit})</th>
                <th style={{ width: "36px" }}></th>
              </tr>
            </thead>
            <tbody>
              {courses.map((c, idx) => {
                const locked = c.locked_minutes != null && !Number.isNaN(c.locked_minutes as any);
                return (
                  <tr key={c.id || idx}>
                    <td>
                      <input ref={(el) => { if (c.id) nameInputRefs.current[c.id] = el; }} type="text" aria-label={`Course name row ${idx + 1}`} value={c.name} onChange={(e) => handleUpdateCourse(idx, { name: e.target.value })} onKeyDown={(e) => handleNameKeyDown(e, idx)} onPaste={(e) => handlePasteSpreadsheet(e, idx)} className="cell-input" placeholder={`Course ${idx + 1}`} />
                    </td>
                    <td>
                      <input type="number" aria-label={`Credits for ${c.name}`} step="0.5" min="0.5" max="1000" value={c.credits} onChange={(e) => handleUpdateCourse(idx, { credits: parseFloat(e.target.value) || 0 })} className="cell-input" />
                    </td>
                    {DIFF_KEYS.map((k) => (
                      <td key={k} className="difficulty-cell">
                        <input type="radio" name={`diff-${c.id || idx}`} aria-label={`${c.name || "Course"} ${ta.difficultyLabels[k].label}`} checked={c.difficulty_level === k} onChange={() => handleUpdateCourse(idx, { difficulty_level: k, custom_difficulty: null })} />
                      </td>
                    ))}
                    <td>
                      <input type="number" aria-label={`Minimum for ${c.name}`} placeholder="—" value={toDisplay(c.min_minutes)} disabled={locked} title={locked ? ta.lockedTooltip : undefined} onChange={(e) => handleUpdateCourse(idx, { min_minutes: fromDisplay(e.target.value) })} className="cell-input" />
                    </td>
                    <td>
                      <input type="number" aria-label={`Maximum for ${c.name}`} placeholder="—" value={toDisplay(c.max_minutes)} disabled={locked} title={locked ? ta.lockedTooltip : undefined} onChange={(e) => handleUpdateCourse(idx, { max_minutes: fromDisplay(e.target.value) })} className="cell-input" />
                    </td>
                    <td>
                      <input type="number" aria-label={`Locked for ${c.name}`} placeholder="—" value={toDisplay(c.locked_minutes)} onChange={(e) => handleUpdateCourse(idx, { locked_minutes: fromDisplay(e.target.value) })} className="cell-input" />
                    </td>
                    <td style={{ textAlign: "center" }}>
                      <button type="button" onClick={() => handleRemoveCourse(idx)} aria-label={`Remove ${c.name}`} style={{ height: "28px", padding: "0 6px", border: "none", background: "transparent", color: "var(--ink-3)" }}>×</button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      <div style={{ display: "flex", gap: "12px", marginTop: "12px", alignItems: "center", flexWrap: "wrap" }}>
        <button type="button" onClick={() => handleAddCourse()}>+ {ta.addCourseButton}</button>
        <button type="button" onClick={() => onCoursesChange([])} style={{ border: "none", color: "var(--ink-2)", height: "36px" }}>{ta.clearButton}</button>
        <span className="font-small" style={{ color: "var(--ink-3)", marginLeft: "auto" }}>{ta.pasteHint}</span>
      </div>

      <div style={{ borderTop: "1px solid var(--rule-soft)", paddingTop: "20px", marginTop: "20px", display: "grid", gridTemplateColumns: "repeat(12, 1fr)", gap: "16px", alignItems: "flex-start" }}>
        <div style={{ gridColumn: "span 4" }}>
          <label className="font-label" style={{ display: "block", marginBottom: "8px" }}>{ta.budgetTitle}</label>
          <div className="toggle-group" style={{ marginBottom: "12px", width: "100%" }}>
            {(["weekly", "daily", "custom"] as BudgetMode[]).map((mode) => (
              <button key={mode} type="button" onClick={() => onBudgetModeChange(mode)} style={{ flex: 1, background: budgetMode === mode ? "var(--ink)" : "transparent", color: budgetMode === mode ? "var(--paper)" : "var(--ink)" }}>{ta.budgetModes[mode]}</button>
            ))}
          </div>
          {budgetMode !== "custom" ? (
            <div>
              <label className="font-label" style={{ display: "block", marginBottom: "6px" }}>Amount ({unit})</label>
              <input type="number" aria-label="Budget amount" step="0.5" min="1" value={toDisplay(budgetAmount)} onChange={(e) => onBudgetAmountChange(fromDisplay(e.target.value) || 0)} style={{ width: "100%" }} />
            </div>
          ) : (
            <div>
              <label className="font-label" style={{ display: "block", marginBottom: "6px" }}>{ta.budgetModes.custom}</label>
              <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
                {customPeriods.map((p, pIdx) => (
                  <div key={pIdx} style={{ display: "flex", gap: "8px" }}>
                    <input type="text" value={p.label} onChange={(e) => { const u = [...customPeriods]; u[pIdx].label = e.target.value; onCustomPeriodsChange(u); }} style={{ flex: 2, height: "34px" }} />
                    <input type="number" value={toDisplay(p.minutes)} onChange={(e) => { const u = [...customPeriods]; u[pIdx].minutes = fromDisplay(e.target.value) || 0; onCustomPeriodsChange(u); }} style={{ flex: 1, height: "34px" }} />
                  </div>
                ))}
                <button type="button" onClick={() => onCustomPeriodsChange([...customPeriods, { label: `Period ${customPeriods.length + 1}`, minutes: 60 }])} style={{ height: "32px", fontSize: "11px" }}>+ Add period</button>
              </div>
            </div>
          )}
        </div>

        <div style={{ gridColumn: "span 3" }}>
          {budgetMode === "daily" && (
            <div>
              <label className="font-label" style={{ display: "block", marginBottom: "6px" }}>{ta.daysPerWeekLabel}</label>
              <input type="number" min="1" max="7" value={daysPerWeek} onChange={(e) => onDaysPerWeekChange(parseInt(e.target.value, 10) || 7)} style={{ width: "100%" }} />
            </div>
          )}
          <div style={{ marginTop: budgetMode === "daily" ? "12px" : "0" }}>
            <label className="font-label" style={{ display: "block", marginBottom: "6px" }}>{ta.unitToggleLabel}</label>
            <div className="toggle-group">
              <button type="button" onClick={() => onUnitChange("min")} style={{ background: unit === "min" ? "var(--ink)" : "var(--paper)", color: unit === "min" ? "var(--paper)" : "var(--ink)" }}>{t.masthead.units.min}</button>
              <button type="button" onClick={() => onUnitChange("h")} style={{ background: unit === "h" ? "var(--ink)" : "var(--paper)", color: unit === "h" ? "var(--paper)" : "var(--ink)" }}>{t.masthead.units.h}</button>
            </div>
          </div>
        </div>

        <div style={{ gridColumn: "span 5" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "10px" }}>
            <input type="checkbox" id="unassigned-easiest" checked={settings.treat_unassigned_as_easiest} onChange={(e) => onSettingsChange({ ...settings, treat_unassigned_as_easiest: e.target.checked })} />
            <label htmlFor="unassigned-easiest" className="font-small" style={{ cursor: "pointer" }}>{ta.unassignedCheckbox}</label>
          </div>
          <button type="button" onClick={() => setShowAdvanced(!showAdvanced)} style={{ height: "32px", padding: "0 12px", border: "1px solid var(--rule-soft)", fontSize: "11px" }}>{showAdvanced ? "− " + ta.advancedToggle : "+ " + ta.advancedToggle}</button>
          {showAdvanced && (
            <div style={{ marginTop: "12px", padding: "14px", border: "1px solid var(--rule-soft)", background: "var(--paper-2)", display: "grid", gridTemplateColumns: "repeat(2, 1fr)", gap: "12px" }}>
              <div>
                <label className="font-label" style={{ display: "block", marginBottom: "4px" }}>{ta.minFloorLabel} ({unit})</label>
                <input type="number" value={toDisplay(settings.min_minutes_per_course)} onChange={(e) => onSettingsChange({ ...settings, min_minutes_per_course: fromDisplay(e.target.value) || 20 })} style={{ width: "100%", height: "34px" }} />
              </div>
              <div style={{ display: "flex", alignItems: "center", gap: "8px", marginTop: "18px" }}>
                <input type="checkbox" id="tie-break-toggle" checked={settings.tie_break} onChange={(e) => onSettingsChange({ ...settings, tie_break: e.target.checked })} />
                <label htmlFor="tie-break-toggle" className="font-small">{ta.tieBreakLabel}</label>
              </div>
              <div style={{ gridColumn: "span 2" }}>
                <label className="font-label" style={{ display: "block", marginBottom: "6px" }}>{ta.difficultyScaleTitle}</label>
                <div className="font-small" style={{ color: "var(--ink-2)", marginBottom: "8px" }}>{ta.difficultyScaleHelp}</div>
                <div style={{ display: "grid", gridTemplateColumns: "repeat(5, 1fr)", gap: "8px" }}>
                  {DIFF_KEYS.map((k) => (
                    <div key={k}>
                      <label className="font-small" style={{ display: "block", marginBottom: "4px" }}>{ta.difficultyLabels[k].label}</label>
                      <input type="number" step="0.05" min="0.1" max="5" value={multipliers[k]} onChange={(e) => updateMultiplier(k, parseFloat(e.target.value) || multipliers[k])} style={{ width: "100%", height: "34px" }} />
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
