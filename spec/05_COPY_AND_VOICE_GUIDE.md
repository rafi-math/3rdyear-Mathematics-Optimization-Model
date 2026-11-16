# 05 · Copy and Voice Guide

Every sentence on the site must read as if a careful person wrote it: a mathematics student who explains things plainly and does not oversell. It must not read as machine-written, and it must not read as marketing.

This file is binding. The agent writes all user-facing text into `frontend/content/strings.ts` and `frontend/content/about.ts`, then audits it against sections 1 to 4 before finishing.

## 1. The voice

- **Plain and specific.** Say what the thing does, with the numbers it uses. "Gives each course at least 20 minutes" beats "ensures balanced coverage".
- **Direct.** Short imperative labels on controls: "Add course", "Run models", "Clear". Statements, not slogans.
- **Modest.** The tool is a model with assumptions. Say what it assumes. Never promise results.
- **One author.** Method, case study and About are first person singular ("I surveyed", "I chose"). The calculator interface is second person and impersonal ("Enter your courses"). Never "we" unless the author supplies a team.
- **British spelling** to match the paper (optimise, programme, minimise). Dates as "18 September 2026".
- **Sentence length varies.** Some sentences are four words. Some run to thirty. Do not settle into one rhythm.
- **No invented backstory.** Do not write anecdotes, feelings, motivations or quotes that the author did not supply. Use only facts from the paper (listed in section 6). Anything else goes in `about.ts` as an empty field for the author, and the About section hides any empty field instead of showing a placeholder.

## 2. Forbidden vocabulary (case-insensitive; the agent greps for each)

delve, dive in, deep dive, unlock, unleash, harness, leverage (as a verb), empower, elevate, supercharge, streamline, seamless, seamlessly, robust, cutting-edge, state-of-the-art, game-changing, revolutionary, transformative, groundbreaking, next-generation, holistic, synergy, ecosystem, landscape (figurative), tapestry, realm, journey (figurative), navigate (figurative), embark, foster, crucial, pivotal, vital, paramount, meticulous, intricate, nuanced, comprehensive (as praise), tailored, curated, effortless, effortlessly, intuitive (as praise), powerful (as praise), smart (as praise), optimal (as praise outside the mathematical sense), "AI-powered", "AI-driven", "at your fingertips", "take your X to the next level", "in today's fast-paced world", "whether you're a … or a …", "look no further", "it's important to note", "it's worth noting", "that said", "ultimately", "in conclusion", "moreover", "furthermore".

"Optimal" and "optimise" are allowed in their mathematical sense, with the thing being optimised named.

## 3. Forbidden structures

- **"Not just X, but Y"** and **"It's not X, it's Y"** contrasts.
- **Triplets as a reflex.** No three-item lists of adjectives or benefits ("fast, simple and powerful"). Lists have as many items as there are things to list.
- **Rhetorical questions as headings** ("Struggling to manage your time?").
- **Em dashes.** Do not use them in interface text. Use a full stop, a comma, a colon or brackets. En dashes are fine in numeric ranges (2021–22).
- **Exclamation marks, emoji, ellipses used for drama.** None.
- **Openers and closers that restate**: no "Here's the thing", no "Let's break it down", no closing line that summarises the paragraph just read.
- **Hedging pile-ups**: "may potentially help to somewhat improve". Say it once or not at all.
- **Colons that set up a reveal** in headings ("The result: ..."). Headings are noun phrases.
- **Title Case in headings.** Sentence case everywhere ("Case study", not "Case Study").
- **Bold or italic emphasis in running text.** The design uses weight and position, not highlighting.
- **Perfect symmetry.** Do not write every card, panel or paragraph to the same length and shape.

## 4. Numbers, units and honesty rules

1. Every number shown is computed from the user's plan or taken from the paper. No sample statistics, no user counts, no "trusted by".
2. Say "minutes" or "hours" in full on first use in a panel, then `min` / `h` in tables.
3. The shadow price is always described with its unit and with the limit on its meaning. Required wording pattern: "One more hour, spent where it counts most, adds *X* to the objective. That is a score inside this model. It is not marks or CGPA."
4. Difficulty is always described as the user's own rating.
5. Model C always carries: "Added for this tool. It is not part of the paper."
6. Never say the tool "improves grades", "boosts performance" or "guarantees" anything.
7. When something is rounded, say so next to the number.

## 5. Reference strings (starting point; the agent may adjust wording but must keep the tone and the rules above)

**Masthead**
- Site name (working title): `Study budget`
- Links: `Calculator` · `Method` · `Case study` · `About` · `Source`
- Unit toggle labels: `MIN` · `H`

**Intro** (display size, then body)
- Statement: `Split your study hours across your courses and see the arithmetic.`
- Body: `Enter your courses, their credits, how hard you find each one, and the hours you actually have. The tool solves a linear programme and shows how much time each course gets under three different rules.`
- Limit line: `It does not predict grades. It measures how well a plan fits the priorities you gave it.`
- Numbered flow: `1  Enter courses and hours` · `2  Add your own rules` · `3  Compare the three models`
- Links: `Go to the calculator ↓` · `Load the case study`

**Calculator, stage A**
- Panel title: `Plan`
- Parser label: `Paste, upload or speak your courses and hours.`
- Parser help: `Text, a screenshot, a PDF or Word file, or a voice note. Nothing is filled in until you have checked it.`
- Buttons: `Read this` · `Record` · `Stop` · `Add course` · `Clear`
- Field labels: `Course` · `Credits` · `Difficulty` · `Minimum` · `Maximum` · `Locked`
- Difficulty labels: `Most difficult` `1.2` · `Difficult` `1.1` · `Medium` `1.0` · `Easy` `0.9` · `Easiest` `0.8`
- Difficulty help: `Your own rating. It is a judgement, not a measurement.`
- Unassigned option: `Treat unassigned courses as Easiest (0.8), as the paper does.`
- Budget: `Time available` · modes `Weekly` `Daily` `Custom periods`
- Empty state: `No courses yet. Add one, or load the case study.`

**Calculator, stage B**
- Panel title: `Rules`
- Help: `Add limits that apply to you. Each rule can be switched off without deleting it.`
- Rule sentences: `At least {time} for {course}.` · `No more than {time} for {course}.` · `Exactly {time} for {course}.` · `Treat {course} as {percent}% more important.` · `At least as much time on {course} as on {course}.` · `{group} together: at most {time}.`

**Calculator, stage C**
- Panel title: `Results`
- Run button: `Run models`
- Out-of-date note: `You have changed the plan since the last run.`
- Rounding note: `Rounded to the minute. The exact total is {total}.`
- Table headers: `Course` · `A · Credits` · `B · Credits × difficulty` · `C · Diminishing returns`
- Model C tag: `Added for this tool. It is not part of the paper.`
- Constraint panel title: `What limited the answer`
- Constraint lines: `The whole budget is used.` · `At the minimum: {courses}.` · `At the cap: {courses}.` · `Left unallocated: {time}.`
- Shadow price title: `Value of one more hour`
- Shadow price body: `One more hour, spent where it counts most, adds {value} to the objective. That is a score inside this model. It is not marks or CGPA. The next hour would go to {courses}.`
- Check line: `Check: re-solving with 30 more minutes changes the objective by {delta}, which is {per_hour} per hour.`
- Exports: `Download CSV` · `Download PDF` · `Add to calendar (.ics)`

**Errors and states**
- Solver asleep: `The solver is starting up. This can take up to a minute.`
- Working: `Working`
- Parse failed: `Could not read that. Paste the text instead, or enter the courses by hand.`
- Parse partial: `Some fields were missing. They are marked below.`
- Parse busy (429): `The reading service is busy. Try again in a minute, or type the plan in.`
- File too large: `That file is over {limit} MB.`
- File type: `This tool reads text, images, PDF, Word and audio files.`
- Infeasible (template): `These rules cannot all hold. {reason} Relax one of them and run again.`
  Example reason: `Ten courses at 20 minutes each need 3 h 20 min, and the budget is 3 h.`
- Offline: `You are offline. Your plan is saved in this browser.`

**Method section** (author voice, first person, short)
- Opening: `The two main models come from my paper. Model A weights each course by its credits. Model B weights it by credits times a difficulty coefficient from five levels, 1.2 down to 0.8. Both maximise the weighted study time, within the same limits.`
- Limits paragraph: `Each course gets at least 20 minutes by default. No course may take more than 1.3 times its proportional share of the budget. Courses with equal weights get equal time, otherwise the solver could choose between them arbitrarily.`
- Model C paragraph: `Model C is not in the paper. I added it because the fifth hour on one subject usually helps less than the first hour on another. The falling values are assumptions I chose, and you can change them.`
- Shadow price paragraph: `The shadow price says how much the objective would rise if the budget grew by one hour. It belongs to the model's own score. It says nothing direct about exam results.`

**Case study drawer**
- Row label: `Case study · Third-year Mathematics, University of Chittagong`
- Paragraph: `I surveyed third-year Mathematics students from the 2021–22 and 2022–23 sessions. 147 of the 200 eligible students replied, a response rate of 73.5%. From their answers I estimated a weekly self-study budget of 7.6 hours, which works out at under 46 minutes per course across ten courses.`
- Table note (paper table): `As printed in the paper. Rounded to the minute, these columns add up to 7 h 40 m and 7 h 34 m. The exact values add up to 7 h 36 m.`
- Limits: `The budget comes from one survey of one group of students. The difficulty ratings came from my own experience and from talking to classmates, so they are not a measured scale. The model is calibrated to this curriculum.`
- Button: `Load case study into calculator`
- Banner after loading: `You are looking at the case study.` + link `Clear and start your own`

**Footer**
- Data note: `Files you upload are read once to fill in the form and are not stored. Your plan stays in this browser.`
- Links: `Source code` · `Paper` · `Contact`

## 6. Facts the About section may use (all from the paper; nothing else may be asserted)

- Name: Md. Ali Arman Rafi
- Department of Mathematics, University of Chittagong, Bangladesh
- Member of the 2021–22 session; did not take part in the survey, to keep the data collection neutral
- The paper: *Optimising a Scarce Study Budget: A Linear Programming Approach to Undergraduate Academic Workload*, dated 18 September 2026
- Method: survey of 147 students, follow-up with the 11 students in the open-ended category, linear programming solved with the Simplex method in Python with PuLP and the CBC solver
- Code, data and figures are public on GitHub: `https://github.com/rafi-math/3rdyear-Mathematics-Optimization-Model`; profile `https://github.com/rafi-math`; email `sbrafi10@gmail.com` (all three appear in the paper)
- Future directions named in the paper: stochastic programming, and a multi-period formulation

Draft About text (author edits before launch; two to four paragraphs, first person):

> `I am a mathematics student at the University of Chittagong. Linear programming was one of our courses, and it struck me that students solve a similar problem every week without writing it down: too little time, too many courses.`

That sentence contains a claim about motivation that the paper only partly supports. The agent must **not** include it as is. It goes into `about.ts` as a suggested draft in a comment for the author to confirm, change or delete. In the live site, show only text drawn from the facts list above, for example:

> `I am a student in the Department of Mathematics at the University of Chittagong. This tool grew out of a paper I wrote on how a third-year student might split a limited weekly study budget across ten courses. The budget came from a survey of 147 classmates. The code and data are public, so anyone can check the work or change the difficulty ratings.`

Add an optional line in `about.ts`, empty by default: `event`, for example the ZRF Science Fair 2026. Hide it when empty.

## 7. Self-audit (agent runs this and reports the result)

1. Grep `strings.ts`, `about.ts`, README and any HTML for every word and phrase in section 2. Zero hits.
2. Grep for `—`, `!`, `…` and emoji ranges. Zero hits in user-facing text.
3. Check that no heading is in Title Case and none ends with a question mark.
4. Read every paragraph aloud and delete any sentence whose removal loses nothing.
5. Check that sentence lengths in the Method and About sections vary, and that no two adjacent paragraphs open the same way.
6. Confirm every number on the page is either computed or traceable to the paper.
7. Confirm there is no placeholder text anywhere. Empty author fields are hidden, not filled.
