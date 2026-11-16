import React, { useState } from "react";
import type { Strings } from "../content/strings";

interface CaseStudyDrawerProps { onLoadCaseStudy: () => void; caseStudyData: any; t: Strings; }

export const CaseStudyDrawer: React.FC<CaseStudyDrawerProps> = ({ onLoadCaseStudy, caseStudyData, t }) => {
  const [isOpen, setIsOpen] = useState(false);
  const cs = t.caseStudy;
  return (
    <section id="case-study" style={{ padding: "24px 0 32px 0" }}>
      <div className="section-rule" />
      <button type="button" onClick={() => setIsOpen(!isOpen)} style={{ width: "100%", padding: "12px 0", border: "none", borderBottom: "1px solid var(--rule)", background: "transparent", display: "flex", justifyContent: "space-between", alignItems: "flex-start", cursor: "pointer", gap: "16px", textAlign: "left" }}>
        <div style={{ display: "flex", alignItems: "flex-start", gap: "16px", flex: 1, minWidth: 0 }}>
          <span className="font-label" style={{ color: "var(--ink-3)", flexShrink: 0, paddingTop: "6px" }}>{cs.sectionNumber}</span>
          <span className="font-h2" style={{ color: "var(--ink)", lineHeight: 1.2, wordBreak: "break-word", paddingBottom: "4px" }}>{cs.rowLabel}</span>
        </div>
        <span className="font-label" style={{ fontSize: "20px", color: "var(--ink)", flexShrink: 0, paddingTop: "4px" }}>{isOpen ? "−" : "+"}</span>
      </button>
      {isOpen && (
        <div style={{ paddingTop: "24px", paddingBottom: "8px" }}>
          <div className="grid-12" style={{ marginBottom: "24px" }}>
            <div style={{ gridColumn: "span 8" }}>
              <p className="font-body" style={{ marginBottom: "20px" }}>{cs.paragraph}</p>
              {caseStudyData?.survey && (
                <div style={{ marginBottom: "24px" }}>
                  <span className="font-label" style={{ display: "block", marginBottom: "8px" }}>{cs.surveyTableTitle}</span>
                  <div className="table-wrap">
                    <table className="data-table">
                      <thead><tr><th className="font-label">RESPONSE CATEGORY</th><th className="font-label" style={{ textAlign: "right" }}>COUNT</th><th className="font-label" style={{ textAlign: "right" }}>PERCENTAGE</th><th className="font-label" style={{ textAlign: "right" }}>MIDPOINT (H/DAY)</th></tr></thead>
                      <tbody>
                        {caseStudyData.survey.categories.map((cat: any, i: number) => (
                          <tr key={i}><td className="font-small">{cat.label}</td><td className="font-figure" style={{ textAlign: "right" }}>{cat.count}</td><td className="font-figure" style={{ textAlign: "right" }}>{cat.pct}%</td><td className="font-figure" style={{ textAlign: "right" }}>{Number(cat.midpoint_h_per_day).toFixed(2)}</td></tr>
                        ))}
                        <tr style={{ borderTop: "2px solid var(--rule)", fontWeight: 600 }}><td className="font-small">Total</td><td className="font-figure" style={{ textAlign: "right" }}>{caseStudyData.survey.respondents}</td><td className="font-figure" style={{ textAlign: "right" }}>100%</td><td className="font-figure" style={{ textAlign: "right" }}>{caseStudyData.survey.weighted_mean_h_per_day} (mean)</td></tr>
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
              {caseStudyData?.paper_table_3_as_printed && (
                <div style={{ marginBottom: "16px" }}>
                  <span className="font-label" style={{ display: "block", marginBottom: "8px" }}>{cs.allocTableTitle}</span>
                  <div className="table-wrap">
                    <table className="data-table">
                      <thead><tr><th className="font-label">COURSE</th><th className="font-label" style={{ textAlign: "right" }}>BASELINE (MODEL A)</th><th className="font-label" style={{ textAlign: "right" }}>IMPROVED (MODEL B)</th></tr></thead>
                      <tbody>
                        {caseStudyData.courses.map((c: any, i: number) => (
                          <tr key={i}><td className="font-small">{c.name}</td><td className="font-figure" style={{ textAlign: "right" }}>{caseStudyData.paper_table_3_as_printed.model_a[i]}</td><td className="font-figure" style={{ textAlign: "right" }}>{caseStudyData.paper_table_3_as_printed.model_b[i]}</td></tr>
                        ))}
                        <tr style={{ borderTop: "2px solid var(--rule)", fontWeight: 600 }}><td className="font-small">Printed total</td><td className="font-figure" style={{ textAlign: "right" }}>{caseStudyData.paper_table_3_as_printed.total}</td><td className="font-figure" style={{ textAlign: "right" }}>{caseStudyData.paper_table_3_as_printed.total}</td></tr>
                      </tbody>
                    </table>
                  </div>
                  <p className="font-small" style={{ color: "var(--ink-2)", marginTop: "8px" }}>{cs.tableNote}</p>
                </div>
              )}
            </div>
            <div style={{ gridColumn: "span 4", display: "flex", flexDirection: "column", gap: "16px" }}>
              <div style={{ border: "1px solid var(--rule)", background: "var(--paper-2)", padding: "16px" }}>
                <span className="font-label" style={{ display: "block", marginBottom: "8px" }}>{cs.limitsTitle}</span>
                <p className="font-small" style={{ color: "var(--ink)", lineHeight: 1.6 }}>{cs.limits}</p>
              </div>
              <div style={{ border: "1px solid var(--rule)", background: "var(--paper-2)", padding: "16px" }}>
                <span className="font-label" style={{ display: "block", marginBottom: "8px" }}>{cs.auditTitle}</span>
                <p className="font-small" style={{ color: "var(--ink)", lineHeight: 1.6 }}>The tool's computed constraint report reveals that four courses reach their proportional cap in Model B (Abstract Algebra, Mechanics, Methods of Applied Mathematics, and Linear Programming), where the case study report's narrative highlights two. The exact solver solution accounts for all four.</p>
              </div>
              <button type="button" className="primary" onClick={onLoadCaseStudy} style={{ width: "100%", height: "44px" }}>{cs.loadButton}</button>
            </div>
          </div>
        </div>
      )}
    </section>
  );
};
