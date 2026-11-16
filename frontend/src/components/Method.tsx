import React from "react";
import type { Strings } from "../content/strings";

interface MethodProps { t: Strings; }

export const Method: React.FC<MethodProps> = ({ t }) => {
  const m = t.method;
  return (
    <section id="method" style={{ padding: "40px 0 48px 0" }}>
      <div className="section-rule" />
      <div className="grid-12" style={{ alignItems: "start" }}>
        <div style={{ gridColumn: "span 3" }}>
          <span className="font-label" style={{ color: "var(--ink-3)" }}>{m.sectionNumber}</span>
          <h2 className="font-h1" style={{ marginTop: "8px", color: "var(--ink)" }}>{m.sectionTitle}</h2>
        </div>
        <div style={{ gridColumn: "span 5", display: "flex", flexDirection: "column", gap: "16px" }}>
          {m.paragraphs.map((p, i) => <p key={i} className="font-body">{p}</p>)}
        </div>
        <div style={{ gridColumn: "span 4", display: "flex", flexDirection: "column", gap: "14px" }}>
          <div style={{ border: "1px solid var(--rule)", background: "var(--paper-2)", padding: "16px" }}>
            <span className="font-label" style={{ color: "var(--ink-2)", display: "block", marginBottom: "8px", lineHeight: 1.4 }}>{m.modelALabel}</span>
            <p className="font-small" style={{ color: "var(--ink)", lineHeight: 1.6 }}>{m.modelADesc}</p>
          </div>
          <div style={{ border: "1px solid var(--rule)", background: "var(--paper-2)", padding: "16px" }}>
            <span className="font-label" style={{ color: "var(--accent)", display: "block", marginBottom: "8px", lineHeight: 1.4 }}>{m.modelBLabel}</span>
            <p className="font-small" style={{ color: "var(--ink)", lineHeight: 1.6 }}>{m.modelBDesc}</p>
          </div>
          <div style={{ border: "1px solid var(--rule)", background: "var(--paper-2)", padding: "16px" }}>
            <span className="font-label" style={{ color: "var(--ink-2)", display: "block", marginBottom: "8px", lineHeight: 1.4 }}>{m.modelCLabel}</span>
            <p className="font-small" style={{ color: "var(--ink)", lineHeight: 1.6 }}>{m.modelCDesc}</p>
            <span className="font-small" style={{ color: "var(--ink-3)", display: "block", marginTop: "8px", fontSize: "12px", lineHeight: 1.5 }}>{m.modelCNote}</span>
          </div>
          <div style={{ border: "1px solid var(--rule)", background: "var(--paper-2)", padding: "16px" }}>
            <span className="font-label" style={{ color: "var(--ink-2)", display: "block", marginBottom: "8px", lineHeight: 1.4 }}>{m.extraTimeLabel}</span>
            <p className="font-small" style={{ color: "var(--ink)", lineHeight: 1.6 }}>{m.extraTimeDesc}</p>
          </div>
        </div>
      </div>
    </section>
  );
};
