import React from "react";
import type { Strings } from "../content/strings";
import { authorFacts } from "../content/about";

interface FooterProps { t: Strings; }

export const Footer: React.FC<FooterProps> = ({ t }) => {
  const f = t.footer;
  return (
    <footer id="colophon" style={{ padding: "40px 0 56px 0" }}>
      <div className="section-rule" />
      <div className="grid-12">
        <div style={{ gridColumn: "span 4" }}>
          <span className="font-label" style={{ color: "var(--ink-3)", display: "block", marginBottom: "8px" }}>{f.sectionNumber} · {f.sectionTitle}</span>
          <div style={{ display: "flex", flexDirection: "column", gap: "8px", marginTop: "10px" }}>
            <a href={authorFacts.githubRepo} target="_blank" rel="noopener noreferrer" className="font-small">{f.links.source} ↗</a>
            <a href="#case-study" className="font-small">{f.links.report}</a>
          </div>
        </div>
        <div style={{ gridColumn: "span 4" }}>
          <span className="font-label" style={{ color: "var(--ink-3)", display: "block", marginBottom: "8px" }}>{f.links.contact}</span>
          <p className="font-small" style={{ color: "var(--ink)" }}>
            {authorFacts.name}<br />
            <a href={`mailto:${authorFacts.email}`}>{authorFacts.email}</a><br />
            {authorFacts.department}, {authorFacts.university}
          </p>
        </div>
        <div style={{ gridColumn: "span 4" }}>
          <span className="font-label" style={{ color: "var(--ink-3)", display: "block", marginBottom: "8px" }}>PRIVACY & DATA HANDLING</span>
          <p className="font-small" style={{ color: "var(--ink-2)" }}>{f.dataNote}</p>
        </div>
      </div>
    </footer>
  );
};
