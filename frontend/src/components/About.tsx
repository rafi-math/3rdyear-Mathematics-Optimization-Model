import React from "react";
import type { Strings } from "../content/strings";
import { authorFacts } from "../content/about";

interface AboutProps { t: Strings; }

export const About: React.FC<AboutProps> = ({ t }) => {
  const a = t.about;
  return (
    <section id="about" style={{ padding: "40px 0 48px 0" }}>
      <div className="section-rule" />
      <div className="grid-12">
        <div style={{ gridColumn: "span 3" }}>
          <span className="font-label" style={{ color: "var(--ink-3)" }}>{a.sectionNumber}</span>
          <h2 className="font-h1" style={{ marginTop: "8px", color: "var(--ink)" }}>{a.sectionTitle}</h2>
        </div>
        <div style={{ gridColumn: "span 5", display: "flex", flexDirection: "column", gap: "16px" }}>
          {authorFacts.bioParagraphs.map((para, i) => <p key={i} className="font-body" style={{ color: "var(--ink)" }}>{para}</p>)}
        </div>
        <div style={{ gridColumn: "span 4" }}>
          <div style={{ border: "1px solid var(--rule)", padding: "20px", background: "var(--paper-2)" }}>
            <span className="font-label" style={{ display: "block", marginBottom: "14px", color: "var(--ink)" }}>{a.factsHeading}</span>
            <dl style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
              {authorFacts.name && <div><dt className="font-label" style={{ color: "var(--ink-3)", fontSize: "10px" }}>AUTHOR</dt><dd className="font-small" style={{ color: "var(--ink)", fontWeight: 500 }}>{authorFacts.name}</dd></div>}
              {authorFacts.department && <div><dt className="font-label" style={{ color: "var(--ink-3)", fontSize: "10px" }}>DEPARTMENT</dt><dd className="font-small" style={{ color: "var(--ink)" }}>{authorFacts.department}</dd></div>}
              {authorFacts.university && <div><dt className="font-label" style={{ color: "var(--ink-3)", fontSize: "10px" }}>UNIVERSITY</dt><dd className="font-small" style={{ color: "var(--ink)" }}>{authorFacts.university}</dd></div>}
              {authorFacts.location && <div><dt className="font-label" style={{ color: "var(--ink-3)", fontSize: "10px" }}>LOCATION</dt><dd className="font-small" style={{ color: "var(--ink)" }}>{authorFacts.location}</dd></div>}
              {authorFacts.reportTitle && <div><dt className="font-label" style={{ color: "var(--ink-3)", fontSize: "10px" }}>CASE STUDY REPORT</dt><dd className="font-small" style={{ color: "var(--ink)" }}>{authorFacts.reportTitle} ({authorFacts.reportDate})</dd></div>}
              {authorFacts.githubRepo && <div><dt className="font-label" style={{ color: "var(--ink-3)", fontSize: "10px" }}>CODE REPOSITORY</dt><dd className="font-small"><a href={authorFacts.githubRepo} target="_blank" rel="noopener noreferrer">github.com/rafi-math ↗</a></dd></div>}
              {authorFacts.email && <div><dt className="font-label" style={{ color: "var(--ink-3)", fontSize: "10px" }}>CONTACT</dt><dd className="font-small"><a href={`mailto:${authorFacts.email}`}>{authorFacts.email}</a></dd></div>}
              {authorFacts.event && <div><dt className="font-label" style={{ color: "var(--ink-3)", fontSize: "10px" }}>EVENT</dt><dd className="font-small" style={{ color: "var(--ink)" }}>{authorFacts.event}</dd></div>}
            </dl>
          </div>
        </div>
      </div>
    </section>
  );
};
