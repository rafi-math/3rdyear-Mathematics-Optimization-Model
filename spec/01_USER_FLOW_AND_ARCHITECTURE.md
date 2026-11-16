# 01 · User Flow and Architecture

## Product in one paragraph

A tool that takes a student's courses (name, credits, difficulty), a time budget and any personal rules, and returns how many minutes or hours each course should get. It runs three optimisation models side by side and explains in plain terms why they differ. The research it is built on is a single case study from a published paper; the tool itself works for any student, any number of courses and any time horizon.

## Hard rule: the PDF is an example, not the dataset

Nothing from the paper may be hardcoded in application logic. The ten Chittagong courses, the 7.6 h budget, the 20-minute floor and the 1.3 cap are **default values in one JSON fixture** (`case-study.json`) that the "Load case study" button feeds into the same form every other user fills in. Delete the fixture and the calculator must still work.

## Information architecture (single page, anchored sections)

Sections are numbered in the page itself (`01`, `02`, ...) in monospace. Order:

| # | Section | Anchor | Purpose |
|---|---|---|---|
| 00 | Masthead | `#top` | Site name, five text links, unit toggle (min / h). No logo graphic |
| 01 | Intro | `#intro` | One short statement of what the tool does and one line on what it does not do |
| 02 | Calculator | `#calculator` | Input, constraints, results. This is the product; it gets the most space |
| 03 | Method | `#method` | The three models, the formulas, how to read the shadow price |
| 04 | Case study | `#case-study` | Collapsible drawer with the paper's survey and results, plus the load button |
| 05 | About | `#about` | The author and the research behind the tool |
| 06 | Footer | `#colophon` | Repository link, contact, a short data-handling note |

No pricing, no testimonials, no "features" grid, no newsletter box.

## The calculator: three stages inside section 02

The stages are shown as three stacked panels with a visible step number. They are not a modal wizard. A user can edit any earlier panel and the later ones recompute.

### Stage A · Plan (input)

Two ways in, side by side on desktop, stacked on mobile:

1. **Describe it** (the multimodal parser): one drop zone that accepts pasted text, an image, a PDF, a DOCX, or a recorded voice note. Plain label: "Paste, upload or speak your courses and hours." Output goes into the form below, never straight to the solver.
2. **Type it**: the form.

The form has:

- **Courses table.** Columns: name, credits (or weight), difficulty, optional min, optional max, optional lock. Add row, remove row, reorder, paste-from-spreadsheet (tab-separated). No cap on rows; warn politely above 30 because the page gets long, not because the solver cannot cope.
- **Difficulty control.** Five levels, shown as labelled segments, not stars and not colours alone:
  `Most difficult 1.2 · Difficult 1.1 · Medium 1.0 · Easy 0.9 · Easiest 0.8`.
  The coefficient is visible next to the label. A "custom coefficient" field is allowed under an Advanced toggle, range 0.5 to 2.0.
  A course with no difficulty chosen is highlighted and blocks the run. See the note on defaults in file 03.
- **Budget.**
  - Mode: `Weekly` · `Daily` · `Custom periods`.
  - Weekly: one number. Daily: one number plus "days per week". Custom periods: a list of dated or named periods, each with its own budget (for example "Mon 90 min, Tue 45 min, Exam week 14 h").
  - Unit toggle (minutes or hours) is global, lives in the masthead and beside the budget field, and converts every number on the page without changing the stored value. Internally everything is minutes.
- **Global settings** (defaults shown, editable): minimum per course (20 min), proportional cap multiplier (1.3), equal-weight courses get equal time (on).

### Stage B · Rules (constraint engine)

A plain list of rules the user adds one at a time. Each rule type has its own small form, and a one-line sentence preview that reads like something a person would say.

| Rule type | Example sentence shown to the user |
|---|---|
| Minimum for a course | "At least 45 min for Calculus." |
| Maximum for a course | "No more than 3 h for History." |
| Lock a block | "Exactly 1 h for Lab Report." |
| Priority boost | "Treat Organic Chemistry as 20% more important." |
| Dependency | "At least as much time on Linear Algebra as on Statistics." (generalised as `x_A ≥ k · x_B`) |
| Group limit | "All language courses together: at most 4 h." |

Every rule can be switched off without deleting it. A rule that makes the problem impossible is flagged immediately and in words (see "Infeasibility" in file 03).

### Stage C · Results (solver output)

Computed on a "Run models" button press, not on every keystroke (solver calls are cheap, but the user should control when numbers change). After the first run, edits mark the results as "out of date" in plain text and keep the old numbers visible until re-run.

Layout of results:

1. **Allocation table.** One row per course, one numeric column per model, tabular figures, right aligned. Time shown in the chosen unit, with the alternative in a lighter weight beside it (e.g. `1 h 24 m` and `84 min`). Total row at the bottom with the exact total and a one-line note about rounding.
2. **Chart.** Horizontal grouped bars, one row per course, one bar per model, direct value labels. Details in file 02.
3. **Why they differ.** A short paragraph per model pair, generated from the numbers by templates (not by a language model), naming the courses that moved and the weight that explains the move.
4. **Constraint status.** A compact table: each active constraint, whether it is binding, the slack in minutes. "Budget fully used", "Minimum reached by: ...", "Cap reached by: ...".
5. **Shadow price.** For each model: the value, the unit it is measured in, and the course that would receive the next extra unit of time. The mandatory sentence about what the number is not: see the copy guide.
6. **Export.** CSV (allocations and constraint status), PDF (one-page summary), `.ics` calendar (see below).

### Multi-period scheduling (Custom periods mode)

The models first decide how much time each course gets over the whole horizon. A second step spreads those totals across the periods without exceeding any period's budget, honouring locks, and keeping each day's mix as close to proportional as possible. Formulation in file 03. The results table gets a period selector and the `.ics` export uses the period split.

## State and data flow

```
[ text | image | PDF | DOCX | audio ]
        │  POST /api/parse
        ▼
  ParsedPlan (JSON, with per-field confidence and source quote)
        │  user reviews and edits the form
        ▼
  Plan (validated JSON)  ──POST /api/solve──▶  SolveResponse (3 models)
        │                                           │
        │                                           ├─▶ results panels
        └──────────────── POST /api/export/* ◀──────┘
```

- The browser holds the plan in memory and in `localStorage` (so a refresh does not lose the form). No accounts, no server-side storage of plans or uploads.
- Uploaded files are processed in memory on the server and discarded when the request ends. Say so in the footer in one plain sentence.

## Stack (fixed, do not substitute without saying why)

| Layer | Choice | Reason |
|---|---|---|
| Front end | Vite + React + TypeScript, plain CSS with custom properties (no Tailwind component kits, no UI library themes) | A kit's default look is what makes sites look generated. Hand-written CSS keeps the grid exact |
| Charts | D3 scales and axes rendered into SVG by React | Full control over hairlines and direct labels |
| Back end | Python 3.11, FastAPI, Pydantic v2 | Typed request and response models |
| Solver | `scipy.optimize.linprog` with the HiGHS method. PuLP with CBC used only in a parity test | HiGHS returns dual values, which gives the shadow price. The paper used PuLP/CBC, so the parity test shows the two agree |
| Parser | Gemini API through a thin provider interface, so another provider can be swapped in | One model handles text, image, audio and PDF |
| Document extraction | `pypdf` for PDF text, `python-docx` for DOCX, with the raw file also passed to the model when text extraction is poor | |
| Exports | `csv` module, `reportlab` for PDF, hand-written `.ics` | No heavy dependencies |
| Tests | `pytest`, `hypothesis` for property tests, Playwright for two end-to-end checks | |

## Error and empty states

Every state has a sentence written for it (see file 05). The agent must not leave framework default messages anywhere. States to cover: solver asleep (free-tier host), parse failed, parse returned partial data, file too large, unsupported file type, infeasible rules, no courses yet, offline.

## Responsive behaviour

- ≥1200 px: twelve-column grid, results table and chart side by side (7 + 5 columns).
- 768 to 1199 px: eight columns, chart below the table.
- <768 px: one column. The courses table becomes stacked cards with each field labelled. The results table becomes one block per course with the three models as labelled lines. No horizontal scrolling for primary content.
- Touch targets at least 44 px. The unit toggle stays reachable from the results.

## Out of scope for v1

Accounts, saved plans on a server, notifications, sharing links, dark mode, languages other than English, a mobile app. Say so in the README, not on the site.
