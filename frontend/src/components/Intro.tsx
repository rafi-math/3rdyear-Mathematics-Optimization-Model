import React from "react";
import type { Strings } from "../content/strings";

interface IntroProps { onLoadCaseStudy: () => void; t: Strings; }

export const Intro: React.FC<IntroProps> = ({ onLoadCaseStudy, t }) => {
  const { statement, body, limitLine, flowSteps, links } = t.intro;
  return (
    <section id="intro" style={{ padding: "40px 0 48px 0" }}>
      <div className="section-rule" />
      <div className="grid-12" style={{ alignItems: "flex-start" }}>
        <div style={{ gridColumn: "span 1" }}><span className="font-label" style={{ color: "var(--ink-3)" }}>01</span></div>
        <div style={{ gridColumn: "span 7" }}>
          <h1 className="font-display" style={{ marginBottom: "24px", color: "var(--ink)" }}>{statement}</h1>
          <p className="font-body" style={{ color: "var(--ink)", marginBottom: "12px" }}>{body}</p>
          <p className="font-body" style={{ color: "var(--ink-2)" }}>{limitLine}</p>
        </div>
        <div style={{ gridColumn: "span 4", paddingTop: "8px" }}>
          <div style={{ borderLeft: "1px solid var(--rule-soft)", paddingLeft: "20px" }}>
            <div style={{ marginBottom: "24px", display: "flex", flexDirection: "column", gap: "12px" }}>
              {flowSteps.map((step, idx) => (<div key={idx} className="font-body" style={{ color: "var(--ink)", fontWeight: 500 }}>{step}</div>))}
            </div>
            <div style={{ display: "flex", flexDirection: "column", gap: "10px", alignItems: "flex-start" }}>
              <a href="#calculator" className="font-small" style={{ fontWeight: 600 }}>{links.goToCalculator}</a>
              <button type="button" onClick={onLoadCaseStudy} className="link-button">{links.loadCaseStudy}</button>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
