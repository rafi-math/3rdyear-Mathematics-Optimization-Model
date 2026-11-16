import React from "react";
import type { ModelResult, SolveResponse, TimeUnit } from "../../types";
import type { Strings } from "../../content/strings";
import { formatTimeWithAlt, formatTimeMinutes, formatTimeHours } from "../../utils/format";
import { AllocationChart } from "./AllocationChart";
import { downloadExport } from "../../api";

interface StageCResultsProps {
  solveResponse: SolveResponse | null;
  isRunning: boolean;
  onRunModels: () => void;
  isOutOfDate: boolean;
  unit: TimeUnit;
  minFloorMinutes: number;
  planPayload: any;
  t: Strings;
}

export const StageC_Results: React.FC<StageCResultsProps> = ({ solveResponse, isRunning, onRunModels, isOutOfDate, unit, minFloorMinutes, planPayload, t }) => {
  const tc = t.stageC;
  const results = solveResponse?.results;
  const resA: ModelResult | undefined = results?.A;
  const resB: ModelResult | undefined = results?.B;
  const resC: ModelResult | undefined = results?.C;

  const handleExport = async (type: "csv" | "pdf" | "ics") => {
    if (!solveResponse || !results) return;
    try {
      await downloadExport(type, { plan: planPayload, results: solveResponse.results, model: "B", schedule: solveResponse.schedule });
    } catch (err: any) {
      alert(err.message || "Export failed.");
    }
  };

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", marginBottom: "20px", flexWrap: "wrap", gap: "12px" }}>
        <div style={{ display: "flex", alignItems: "baseline", gap: "16px", flexWrap: "wrap" }}>
          <span className="font-label" style={{ color: "var(--ink-3)" }}>{tc.stepNumber}</span>
          <h3 className="font-h3">{tc.title}</h3>
          <span className="font-small" style={{ color: "var(--ink-2)" }}>{tc.subtitle}</span>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
          {isOutOfDate && solveResponse && <span className="font-small" style={{ color: "var(--warn)" }}>! {t.calculator.outOfDateNotice}</span>}
          <button type="button" className="primary" onClick={onRunModels} disabled={isRunning}>{isRunning ? t.calculator.loadingNotice : t.calculator.runButton}</button>
        </div>
      </div>

      {solveResponse?.status === "infeasible" && (
        <div role="alert" style={{ border: "1px solid var(--warn)", padding: "20px", background: "var(--paper-2)", marginBottom: "24px" }}>
          <div style={{ color: "var(--warn)", fontWeight: 600, marginBottom: "8px" }} className="font-h3">! {tc.infeasibleTitle}</div>
          <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
            {solveResponse.reasons.map((r, i) => <p key={i} className="font-body">{r}</p>)}
            {solveResponse.suggestions.map((s, i) => <p key={i} className="font-small" style={{ color: "var(--ink-2)" }}>Suggestion: {s}</p>)}
          </div>
        </div>
      )}

      {solveResponse?.status === "optimal" && resA && resB && (
        <div>
          <div className="grid-12" style={{ marginBottom: "32px", alignItems: "flex-start" }}>
            <div style={{ gridColumn: "span 7" }}>
              <div className="table-wrap">
                <table className="data-table" style={{ textAlign: "right" }}>
                  <thead>
                    <tr>
                      <th className="font-label" style={{ textAlign: "left" }}>{tc.tableHeaders.course}</th>
                      <th className="font-label">{tc.tableHeaders.modelA}</th>
                      <th className="font-label" style={{ color: "var(--accent)" }}>{tc.tableHeaders.modelB}</th>
                      {resC && <th className="font-label" style={{ color: "var(--ink-2)" }}>{tc.tableHeaders.modelC}</th>}
                    </tr>
                  </thead>
                  <tbody>
                    {resA.allocations.map((aItem, idx) => {
                      const bItem = resB.allocations[idx];
                      const cItem = resC?.allocations[idx];
                      const altA = formatTimeWithAlt(aItem.minutes, unit);
                      const altB = bItem ? formatTimeWithAlt(bItem.minutes, unit) : null;
                      const altC = cItem ? formatTimeWithAlt(cItem.minutes, unit) : null;
                      return (
                        <tr key={idx}>
                          <td style={{ textAlign: "left" }} className="font-small">{aItem.course_name}</td>
                          <td className="font-figure">
                            <span>{altA.primary}</span>
                            {altA.secondary && <span style={{ color: "var(--ink-3)", marginLeft: "6px", fontSize: "11px" }}>{altA.secondary}</span>}
                            {aItem.is_max_allocation && <span style={{ marginLeft: "4px" }}>▲</span>}
                            {aItem.is_min_allocation && <span style={{ marginLeft: "4px" }}>▼</span>}
                          </td>
                          <td className="font-figure">
                            {altB && (<><span style={{ color: "var(--accent)", fontWeight: 500 }}>{altB.primary}</span>{altB.secondary && <span style={{ color: "var(--ink-3)", marginLeft: "6px", fontSize: "11px" }}>{altB.secondary}</span>}{bItem?.is_max_allocation && <span style={{ marginLeft: "4px" }}>▲</span>}{bItem?.is_min_allocation && <span style={{ marginLeft: "4px" }}>▼</span>}</>)}
                          </td>
                          {resC && (
                            <td className="font-figure">
                              {altC && (<><span style={{ color: "var(--ink-2)" }}>{altC.primary}</span>{altC.secondary && <span style={{ color: "var(--ink-3)", marginLeft: "6px", fontSize: "11px" }}>{altC.secondary}</span>}{cItem?.is_max_allocation && <span style={{ marginLeft: "4px" }}>▲</span>}{cItem?.is_min_allocation && <span style={{ marginLeft: "4px" }}>▼</span>}</>)}
                            </td>
                          )}
                        </tr>
                      );
                    })}
                    <tr style={{ borderTop: "2px solid var(--rule)" }}>
                      <td style={{ textAlign: "left", fontWeight: 600 }} className="font-small">Total</td>
                      <td style={{ fontWeight: 600 }} className="font-figure">{unit === "min" ? formatTimeMinutes(resA.total_minutes) : formatTimeHours(resA.total_minutes)}</td>
                      <td style={{ fontWeight: 600, color: "var(--accent)" }} className="font-figure">{unit === "min" ? formatTimeMinutes(resB.total_minutes) : formatTimeHours(resB.total_minutes)}</td>
                      {resC && <td style={{ fontWeight: 600, color: "var(--ink-2)" }} className="font-figure">{unit === "min" ? formatTimeMinutes(resC.total_minutes) : formatTimeHours(resC.total_minutes)}</td>}
                    </tr>
                  </tbody>
                </table>
              </div>
              <div className="font-small" style={{ marginTop: "10px", color: "var(--ink-3)" }}>{tc.roundingNote.replace("{total}", formatTimeHours(resB.total_minutes))}</div>
            </div>
            <div style={{ gridColumn: "span 5", borderLeft: "1px solid var(--rule-soft)", paddingLeft: "20px" }}>
              <AllocationChart allocationsA={resA.allocations} allocationsB={resB.allocations} allocationsC={resC?.allocations} minFloorMinutes={minFloorMinutes} unit={unit} />
            </div>
          </div>

          {solveResponse.explanations && solveResponse.explanations.length > 0 && (
            <div style={{ borderTop: "1px solid var(--rule)", paddingTop: "24px", marginBottom: "28px" }}>
              <span className="font-label" style={{ display: "block", marginBottom: "10px" }}>{tc.whyDifferTitle}</span>
              <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>{solveResponse.explanations.map((exp, idx) => <p key={idx} className="font-body">{exp}</p>)}</div>
            </div>
          )}

          {resB.constraints && resB.constraints.length > 0 && (
            <div style={{ borderTop: "1px solid var(--rule-soft)", paddingTop: "24px", marginBottom: "28px" }}>
              <span className="font-label" style={{ display: "block", marginBottom: "12px" }}>{tc.constraintsTitle}</span>
              <div className="table-wrap">
                <table className="data-table">
                  <thead><tr><th className="font-label">{tc.limitColumn}</th><th className="font-label">{tc.detailColumn}</th><th className="font-label" style={{ textAlign: "right" }}>{tc.leftoverColumn}</th><th className="font-label" style={{ textAlign: "right" }}>{tc.statusColumn}</th></tr></thead>
                  <tbody>
                    {resB.constraints.map((c, i) => (
                      <tr key={i}>
                        <td className="font-small" style={{ fontWeight: c.is_binding ? 600 : 400 }}>{c.name}</td>
                        <td className="font-small" style={{ color: "var(--ink-2)" }}>{c.description}</td>
                        <td className="font-figure" style={{ textAlign: "right" }}>{unit === "min" ? `${c.slack_minutes.toFixed(1)} min` : `${(c.slack_minutes / 60).toFixed(2)} h`}</td>
                        <td className="font-label" style={{ textAlign: "right", color: c.is_binding ? "var(--accent)" : "var(--ink-3)" }}>{c.is_binding ? tc.statusFull : tc.statusRoom}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          <div style={{ display: "flex", gap: "12px", flexWrap: "wrap", borderTop: "1px solid var(--rule)", paddingTop: "20px" }}>
            <button type="button" onClick={() => handleExport("csv")}>↓ {tc.exportButtons.csv}</button>
            <button type="button" onClick={() => handleExport("pdf")}>↓ {tc.exportButtons.pdf}</button>
            <button type="button" onClick={() => handleExport("ics")}>↓ {tc.exportButtons.ics}</button>
          </div>
        </div>
      )}
    </div>
  );
};
