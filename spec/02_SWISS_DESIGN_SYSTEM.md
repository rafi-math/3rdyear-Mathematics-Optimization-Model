# 02 · Swiss Editorial Design System

Direction: Swiss International Style, in the manner of Josef Müller-Brockmann and the quantitative print journals. Flush-left, ragged-right text. A strict grid. One accent colour. Numbers treated as the main content, not decoration.

**Precedence:** if the attached demo image disagrees with this file on spacing, density or section order, follow the image. Colour tokens, typography and the forbidden list below always come from this file.

## 1. Tokens

```css
:root {
  /* Surfaces */
  --paper:      #F5F3EE;   /* page background, warm off-white */
  --paper-2:    #ECE9E1;   /* table zebra is NOT used; this is for the code/formula well only */
  --ink:        #111111;   /* text, primary rules, primary button */
  --ink-2:      #4A4A46;   /* secondary text (contrast on paper ≈ 8:1) */
  --ink-3:      #77746C;   /* tertiary, captions only, 16px and above (≈ 4.5:1) */
  --rule:       #111111;   /* structural 1px rules */
  --rule-soft:  #CFCBC0;   /* inner hairlines inside tables */

  /* One accent */
  --accent:     #CC3300;   /* vermilion. White on it ≈ 5.2:1, on paper ≈ 4.7:1 */

  /* Chart series (never rely on colour alone, see §6) */
  --series-a:   #111111;   /* Model A, solid */
  --series-b:   #CC3300;   /* Model B, solid */
  --series-c:   #8A8578;   /* Model C, solid mid grey */

  /* Status (text + symbol, never colour alone) */
  --ok:         #111111;
  --warn:       #CC3300;

  /* Geometry */
  --u:          8px;       /* baseline unit */
  --gutter:     24px;
  --margin:     32px;      /* 16px below 768px */
  --maxw:       1440px;
  --radius:     0;         /* no rounded corners anywhere, except form focus: none */
}
```

There is no dark mode in v1. There are no gradients, no shadows, no blur, no opacity tricks for depth.

Accent usage budget: at most **one accent element per viewport**, apart from chart series B. Allowed uses: the current section number, the selected difficulty segment, the "out of date" notice, a binding-constraint marker, the focus of an error. Not allowed: large coloured backgrounds, coloured headings, coloured links in body text (links are underlined ink).

## 2. Typography

| Role | Family | Notes |
|---|---|---|
| Text and headings | `Inter` (variable) with fallback `"Helvetica Neue", Helvetica, Arial, sans-serif` | Self-host the font files; do not load from a CDN at runtime |
| Numbers, labels, section numbers, units | `JetBrains Mono` with fallback `"IBM Plex Mono", ui-monospace, monospace` | |

Always set `font-variant-numeric: tabular-nums` on tables, inputs and results. `font-feature-settings: "ss01", "cv11"` is allowed on Inter; do not enable decorative alternates.

Scale (px / line-height / weight / tracking). Line heights are multiples of 8 or 4.

| Token | Size / LH | Weight | Use |
|---|---|---|---|
| `display` | 88 / 88 | 600 | Intro statement only, desktop. Tracking −0.03em |
| `h1` | 56 / 56 | 600 | Section titles. −0.02em |
| `h2` | 32 / 40 | 600 | Sub-sections. −0.01em |
| `h3` | 20 / 28 | 600 | Panel titles |
| `body` | 17 / 28 | 400 | Running text. Max line length 64 characters |
| `small` | 14 / 20 | 400 | Table cells, helper text |
| `label` (mono) | 12 / 16 | 500 | UPPERCASE, +0.06em, field labels and section numbers |
| `figure` (mono) | 14 / 20 | 500 | Numbers in tables |
| `figure-xl` (mono) | 64 / 64 | 500 | Shadow price value |

Mobile: `display` 44/44, `h1` 36/40, `h2` 26/32, others unchanged.

Text is flush left, ragged right. No justified text, no centred paragraphs, no centred headings. Hyphenation off. Use real typographic quotes and the true minus sign (−) in numbers.

## 3. Grid

- 12 columns, 24 px gutters, 32 px outer margins, max width 1440 px, centred.
- Baseline unit 8 px. Vertical spacing between blocks is 8 × {1, 2, 3, 5, 8, 13}.
- Each section opens with a **1 px ink rule across the full content width**, then the section number in mono in column 1, the title starting in column 3. This is the main structural device of the page.
- Asymmetry is intentional: titles sit in columns 3 to 8, running text in columns 3 to 8 or 9 to 12, never both centred. Large areas of empty paper are expected.
- Add an optional grid overlay toggled by pressing `G` (development aid; keep it in the build, off by default). Twelve 1 px vertical lines in `--rule-soft`.

## 4. Page composition

### 00 Masthead (64 px high)

Left: the site name in `label` style. Centre-left: five text links (Calculator, Method, Case study, About, Source). Right: the unit toggle `MIN | H` as two adjoining rectangles, selected one filled ink with paper text. A 1 px ink rule below. Not sticky on desktop. On mobile it collapses to name + menu button that opens a plain full-width list.

### 01 Intro

Asymmetric. Columns 1 to 8: the `display` statement (see file 05 for the exact strings). Columns 9 to 12, aligned to the baseline of the statement's last line: three short numbered lines in `body` describing the flow (1 Enter courses · 2 Set rules · 3 Compare models). Under it, a single text link "Go to calculator ↓" and a text link "Load the case study". No illustration, no image, no animated element.

### 02 Calculator

- Panel title row: step number in mono, `h3` title, a one-line description in `small`.
- Courses table: header row `label` style, 1 px ink rule under header, `rule-soft` rules between rows, no vertical rules, no cell fills. Inputs are borderless inside the table and show a 1 px ink underline on focus; the whole row gets no highlight colour.
- Standalone inputs: 1 px solid ink rectangle, 48 px high, 12 px horizontal padding, background `--paper`. Focus: 2 px ink outline, 2 px offset. Error: 1 px accent border plus an error sentence below with a `!` glyph in mono.
- Difficulty segmented control: five adjoining rectangles, label on top line, coefficient in mono on the second line. Selected: ink fill, paper text. Hover: 1 px inset ink line. Selected state in the *accent* is allowed only when the control has an error.
- Buttons: rectangular, 48 px high, 24 px side padding, 1 px ink border, `label` text. Primary = ink fill, paper text. Hover = invert (paper fill, ink text). Only one primary button visible per panel. No icons inside buttons except `↓` and `↗` text glyphs.
- Results table: right-aligned numbers, units in the column header not in every cell, a thick 2 px ink rule above the total row. The lowest-allocation and highest-allocation cells in each model column are marked with `▲` and `▼` mono glyphs, not with colour.

### 03 Method

Two-column editorial layout. Left (cols 3 to 8): explanation text. Right (cols 9 to 12): formulas in a `--paper-2` well with 1 px ink border, set in mono or in KaTeX using a serif-free math font that matches Inter. Each model has a numbered heading `A`, `B`, `C`. A worked example uses the case-study numbers only if they are labelled as such.

### 04 Case study drawer

Closed by default, opened with a full-width row: `04  Case study · Third-year Mathematics, University of Chittagong   +`. Open state shows, in this order: one paragraph on the survey; Table 1 (the survey distribution) as a real table; the allocation results for the two paper models as a real table; the shadow price; a note on the limits of the study; the button `Load case study into calculator`. After the click the page scrolls to the calculator, fills it and runs the models. A one-line banner at the top of the calculator says the plan is the case study, with a link `Clear and start your own`.

### 05 About

Cols 1 to 2: label `ABOUT`. Cols 3 to 8: the author's text in `body`, 2 to 4 short paragraphs. Cols 9 to 12: a small facts list in mono (Name, Department, University, Paper, Code), each value a plain link where one exists. A square portrait is allowed **only if the author supplies a photograph**; otherwise no image and no initials avatar. No social icon row.

### 06 Footer

Three columns of `small` text: source links, contact, data note. One rule above.

## 5. Chart specification

- Horizontal grouped bars. Row height 40 px, bar thickness 12 px, 4 px between bars in a row.
- No gridlines except a 1 px `--rule-soft` line at each axis tick; no box around the plot.
- X axis: hairline, ticks every 15 or 30 minutes depending on the maximum, tick labels in mono `small`. Axis label states the unit.
- Value labels at the end of each bar, mono, 12 px. No legend box: label the series once, directly, above the first row (`A · Credits`, `B · Credits × difficulty`, `C · Diminishing returns`).
- The minimum floor is drawn as a 1 px dashed ink vertical line labelled `Minimum`.
- Colour is never the only carrier of meaning: series A is solid ink, series B is solid vermilion, series C is mid grey with a 1 px ink outline. Printing in greyscale must still separate them (A black, B dark grey, C light grey).
- Hover or focus on a row shows a one-line readout under the chart, not a floating tooltip card.
- Transition on first draw: bars grow from zero in 240 ms, `ease-out`. Disabled under `prefers-reduced-motion`.
- Provide an accessible text alternative: the allocation table is the equivalent, and the chart has `role="img"` with an `aria-describedby` pointing to a sentence summary.

## 6. Motion and interaction

Duration 120 ms for state changes, 240 ms for the chart draw and the drawer. Easing `cubic-bezier(0.2, 0, 0, 1)`. No bounce, no parallax, no scroll-triggered fades, no cursor effects, no skeleton shimmer (use the text "Working" in mono with a static dotted rule). Respect `prefers-reduced-motion`.

## 7. Accessibility

WCAG 2.2 AA. Visible focus on everything. All form controls have visible labels. Error text is announced via `aria-live="polite"`. The unit toggle is a real `role="radiogroup"`. Keyboard: the courses table supports `Enter` to add a row and `Backspace` on an empty name to remove it. Colour contrast verified in CI with an automated check (axe via Playwright).

## 8. Forbidden list (the agent must grep its own output against this)

- Gradients of any kind, purple / blue / neon colours, glassmorphism, backdrop blur, glow, soft or coloured drop shadows
- Rounded corners, pill buttons, circular avatars, rounded cards
- Hero illustrations, 3D shapes, floating mockups, blobs, abstract mesh backgrounds, stock photography
- Sparkle glyphs, rocket and lightbulb icons, emoji anywhere in the interface
- Icon libraries used as decoration; the only glyphs permitted are `↓ ↗ + − ▲ ▼ !` rendered as text
- Bounce, spring and elastic animation; counters that count up; typewriter effects
- Pricing tables, feature grids with icons, logo walls, testimonial carousels, "trusted by" strips, badge rows
- Placeholder text of any kind: lorem ipsum, "Your name here", sample metrics, invented user counts, made-up statistics
- Any chart or number that is not computed from the user's current plan or from the PDF case study
- UI kit default themes (shadcn defaults, Material, Bootstrap, DaisyUI) left unmodified

## 9. Review checklist (agent runs it before calling the UI done)

1. Does every section start with a full-width ink rule and a mono number?
2. Is there exactly one accent element in each viewport (chart series aside)?
3. Are all numbers tabular and right-aligned in tables?
4. Is every corner square?
5. Is every sentence on the page written according to file 05?
6. Do the screenshots at 1440, 1024, 768 and 390 px keep the grid intact?
7. Does the greyscale print preview still distinguish the three series?
