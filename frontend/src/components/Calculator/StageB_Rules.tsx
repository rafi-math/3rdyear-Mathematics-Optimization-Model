import React, { useMemo, useState } from "react";
import type { Course, Rule, RuleType, TimeUnit } from "../../types";
import type { Strings } from "../../content/strings";

interface StageBRulesProps {
  rules: Rule[];
  onRulesChange: (rules: Rule[]) => void;
  courses: Course[];
  unit: TimeUnit;
  t: Strings;
}

const fmt = (mins: number, unit: TimeUnit) => unit === "min" ? `${Math.round(mins)} min` : `${(mins / 60).toFixed(2)} h`;

export const StageB_Rules: React.FC<StageBRulesProps> = ({ rules, onRulesChange, courses, unit, t }) => {
  const tb = t.stageB;
  const [newType, setNewType] = useState<RuleType>("min");
  const [courseA, setCourseA] = useState<string>("");
  const [courseB, setCourseB] = useState<string>("");
  const [ruleTime, setRuleTime] = useState<string>("45");
  const [boostPct, setBoostPct] = useState<string>("20");
  const [depK, setDepK] = useState<string>("1.0");

  const courseNames = courses.map(c => c.name).filter(Boolean);
  const resolvedA = courseA || courseNames[0] || "";
  const resolvedB = courseB || courseNames[1] || courseNames[0] || "";

  const tableRules = useMemo(() => rules.filter(r => String(r.id || "").startsWith("tbl-")), [rules]);
  const userRules = useMemo(() => rules.filter(r => !String(r.id || "").startsWith("tbl-")), [rules]);

  const getRuleSentence = (r: Rule): string => {
    const timeFormatted = r.time_minutes != null ? fmt(r.time_minutes, unit) : `0 ${unit}`;
    switch (r.type) {
      case "min": return `At least ${timeFormatted} for ${r.course_id}.`;
      case "max": return `No more than ${timeFormatted} for ${r.course_id}.`;
      case "lock": return `Exactly ${timeFormatted} for ${r.course_id}.`;
      case "boost": { const pct = r.boost_factor ? Math.round((r.boost_factor - 1) * 100) : 0; return `Treat ${r.course_id} as ${pct}% more important.`; }
      case "dependency": { const kStr = r.dependency_k && r.dependency_k !== 1 ? ` (${r.dependency_k}×)` : ""; return `At least as much time on ${r.course_id} as on ${r.target_course_id}${kStr}.`; }
      case "group_limit": { const groupStr = (r.group_course_ids || []).join(", "); return `${groupStr} together: at most ${timeFormatted}.`; }
      case "unavailable": return `${r.course_id} is unavailable in period ${r.period_label}.`;
      default: return "Custom rule.";
    }
  };

  const handleAddRule = () => {
    if (courseNames.length === 0) return;
    const timeVal = parseFloat(ruleTime) || 0;
    const timeMinutes = unit === "min" ? timeVal : timeVal * 60;
    const newRule: Rule = {
      id: `rule-${Date.now()}`, type: newType, enabled: true,
      course_id: resolvedA,
      target_course_id: newType === "dependency" ? resolvedB : undefined,
      time_minutes: ["min", "max", "lock", "group_limit"].includes(newType) ? timeMinutes : undefined,
      boost_factor: newType === "boost" ? 1 + (parseFloat(boostPct) || 0) / 100 : undefined,
      dependency_k: newType === "dependency" ? parseFloat(depK) || 1.0 : undefined,
    };
    onRulesChange([...userRules, newRule, ...tableRules]);
  };

  const handleToggleRule = (id: string) => onRulesChange(rules.map(r => r.id === id ? { ...r, enabled: !r.enabled } : r));
  const handleDeleteRule = (id: string) => onRulesChange(userRules.filter(r => r.id !== id).concat(tableRules));

  return (
    <div style={{ marginBottom: "40px" }}>
      <div style={{ display: "flex", alignItems: "baseline", gap: "16px", marginBottom: "20px", flexWrap: "wrap" }}>
        <span className="font-label" style={{ color: "var(--ink-3)" }}>{tb.stepNumber}</span>
        <h3 className="font-h3">{tb.title}</h3>
        <span className="font-small" style={{ color: "var(--ink-2)" }}>{tb.subtitle}</span>
      </div>

      {tableRules.length > 0 && (
        <div style={{ marginBottom: "16px" }}>
          <span className="font-small" style={{ color: "var(--ink-2)", display: "block", marginBottom: "8px" }}>{tb.syncedNote}</span>
          <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
            {tableRules.map(r => (
              <div key={r.id} style={{ display: "flex", alignItems: "center", gap: "12px", padding: "8px 12px", border: "1px solid var(--rule-soft)", background: "var(--paper-2)" }}>
                <span className="font-small" style={{ color: "var(--ink)" }}>{getRuleSentence(r)}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      <div style={{ marginBottom: "20px" }}>
        {userRules.length === 0 ? (
          <div style={{ padding: "18px", border: "1px dashed var(--rule-soft)", color: "var(--ink-3)" }} className="font-small">{tb.emptyState}</div>
        ) : (
          <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
            {userRules.map(r => (
              <div key={r.id} style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "10px 14px", border: "1px solid var(--rule-soft)", background: r.enabled ? "var(--paper)" : "var(--paper-2)", opacity: r.enabled ? 1 : 0.6 }}>
                <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
                  <input type="checkbox" checked={r.enabled} onChange={() => handleToggleRule(r.id!)} aria-label={`Toggle ${getRuleSentence(r)}`} />
                  <span className="font-small" style={{ color: "var(--ink)" }}>{getRuleSentence(r)}</span>
                </div>
                <button type="button" onClick={() => handleDeleteRule(r.id!)} style={{ height: "28px", padding: "0 8px", border: "none", background: "transparent", color: "var(--ink-3)", fontSize: "12px" }}>{tb.delete}</button>
              </div>
            ))}
          </div>
        )}
      </div>

      {courses.length > 0 && (
        <div style={{ border: "1px solid var(--rule)", padding: "16px", background: "var(--paper-2)" }}>
          <span className="font-label" style={{ display: "block", marginBottom: "12px" }}>Add a personal constraint</span>
          <div style={{ display: "flex", flexWrap: "wrap", gap: "10px", alignItems: "center" }}>
            <select value={newType} onChange={(e) => setNewType(e.target.value as RuleType)} style={{ height: "36px", background: "var(--paper)" }}>
              <option value="min">{tb.ruleTypes.min}</option>
              <option value="max">{tb.ruleTypes.max}</option>
              <option value="lock">{tb.ruleTypes.lock}</option>
              <option value="boost">{tb.ruleTypes.boost}</option>
              <option value="dependency">{tb.ruleTypes.dependency}</option>
            </select>
            <select value={resolvedA} onChange={(e) => setCourseA(e.target.value)} style={{ height: "36px", background: "var(--paper)" }}>
              {courseNames.map((n, i) => <option key={i} value={n}>{n}</option>)}
            </select>
            {["min", "max", "lock"].includes(newType) && (
              <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                <input type="number" value={ruleTime} onChange={(e) => setRuleTime(e.target.value)} style={{ width: "80px", height: "36px" }} />
                <span className="font-label">{unit}</span>
              </div>
            )}
            {newType === "boost" && (
              <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                <input type="number" value={boostPct} onChange={(e) => setBoostPct(e.target.value)} style={{ width: "70px", height: "36px" }} />
                <span className="font-label">%</span>
              </div>
            )}
            {newType === "dependency" && (
              <>
                <span className="font-small">as on</span>
                <select value={resolvedB} onChange={(e) => setCourseB(e.target.value)} style={{ height: "36px", background: "var(--paper)" }}>
                  {courseNames.map((n, i) => <option key={i} value={n}>{n}</option>)}
                </select>
                <input type="number" step="0.1" min="0.1" value={depK} onChange={(e) => setDepK(e.target.value)} style={{ width: "64px", height: "36px" }} />
                <span className="font-label">×</span>
              </>
            )}
            <button type="button" className="primary" onClick={handleAddRule} style={{ height: "36px", marginLeft: "auto" }}>{tb.addRuleButton}</button>
          </div>
        </div>
      )}
    </div>
  );
};
