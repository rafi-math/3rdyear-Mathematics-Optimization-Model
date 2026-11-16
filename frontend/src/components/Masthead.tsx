import React from "react";
import type { Lang, Strings } from "../content/strings";

interface MastheadProps {
  lang: Lang;
  onLangChange: (lang: Lang) => void;
  theme: "light" | "dark";
  onThemeChange: (theme: "light" | "dark") => void;
  t: Strings;
}

export const Masthead: React.FC<MastheadProps> = ({ lang, onLangChange, theme, onThemeChange, t }) => {
  const { siteName, navLinks } = t.masthead;
  return (
    <header id="top" className="masthead">
      <div className="masthead-left">
        <a href="#top" className="font-label" style={{ textDecoration: "none", color: "var(--ink)", fontWeight: 600, fontSize: "13px", letterSpacing: "0.08em" }}>
          {siteName}
        </a>
        <nav aria-label="Main navigation" className="masthead-nav">
          {navLinks.map((link) => (
            <a key={link.id} href={link.href} className="font-small" target={link.href.startsWith("http") ? "_blank" : undefined} rel={link.href.startsWith("http") ? "noopener noreferrer" : undefined} style={{ textDecoration: "none", color: "var(--ink-2)" }}>
              {link.label}{link.href.startsWith("http") ? " ↗" : ""}
            </a>
          ))}
        </nav>
      </div>
      <div className="masthead-controls">
        <div className="toggle-group" role="radiogroup" aria-label={t.masthead.langLabel}>
          <button type="button" role="radio" aria-checked={lang === "en"} onClick={() => onLangChange("en")} style={{ background: lang === "en" ? "var(--ink)" : "var(--paper)", color: lang === "en" ? "var(--paper)" : "var(--ink)" }}>EN</button>
          <button type="button" role="radio" aria-checked={lang === "bn"} onClick={() => onLangChange("bn")} style={{ background: lang === "bn" ? "var(--ink)" : "var(--paper)", color: lang === "bn" ? "var(--paper)" : "var(--ink)" }}>বাংলা</button>
        </div>
        <button type="button" className="icon-btn" aria-label={theme === "dark" ? t.masthead.themeLight : t.masthead.themeDark} title={theme === "dark" ? t.masthead.themeLight : t.masthead.themeDark} onClick={() => onThemeChange(theme === "dark" ? "light" : "dark")}>
          {theme === "dark" ? "☀" : "☾"}
        </button>
      </div>
    </header>
  );
};
