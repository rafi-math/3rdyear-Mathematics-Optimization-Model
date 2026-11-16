# Understanding of Research Paper, Demo Reference, and Specifications

## (a) Formulas Extracted from the Paper (with PDF Equation Numbers)

From *Optimising a Scarce Study Budget: A Linear Programming Approach to Undergraduate Academic Workload* (Md. Ali Arman Rafi, 18 Sep 2026):

1. **Equation (1) · Corrected Midpoint for Open-Ended Category (4 hours or above):**
   $$m_{4\text{h}+} = \frac{2 \times 6 + 4 \times 5 + 5 \times 4}{11} = \frac{52}{11} \approx 4.727\text{ h/day}$$

2. **Equation (2) · Weighted Mean Daily Self-Study Time:**
   $$\bar{h}_{\text{daily}} = \frac{\sum_{k=1}^5 n_k m_k}{n} = \frac{7(0.25) + 38(0.75) + 31(2.5) + 11(4.727) + 60(0)}{147} = \frac{159.75}{147} \approx 1.087\text{ h/day}$$
   Multiplying by 7 days gives the weekly budget:
   $$\text{LP Budget} = 7.6\text{ h/week} = 456\text{ min/week}$$

3. **Equation (3) · Model A Objective Function (Baseline, weighted by credits only):**
   $$\max Z_{\text{base}} = \sum_{i=1}^{10} c_i \cdot x_i$$
   where $c_i$ is course credits and $x_i$ is weekly study time allocated to course $i$.

4. **Equation (4) · Model B Objective Function (Improved, weighted by credits times difficulty):**
   $$\max Z_{\text{imp}} = \sum_{i=1}^{10} c_i \cdot d_i \cdot x_i$$
   where $d_i \in \{1.2, 1.1, 1.0, 0.9, 0.8\}$ corresponds to {Most Difficult, Difficult, Medium, Easy, Easiest}.

5. **Equation (5) · Constraint C1 (Weekly Budget):**
   $$\sum_{i=1}^{10} x_i \le 7.6\text{ h} \quad (\text{or } 456\text{ min})$$

6. **Equation (6) · Constraint C2 (Minimum Coverage):**
   $$x_i \ge \frac{1}{3}\text{ h} = 20\text{ min}, \quad \forall i$$

7. **Equation (7) · Constraint C3 (Proportional Upper Bound / Cap):**
   $$x_i \le \frac{w_i}{\sum_{j} w_j} \times 7.6 \times 1.3, \quad \forall i$$
   where $w_i = c_i$ (Baseline Model A) or $w_i = c_i d_i$ (Improved Model B), with cap multiplier $\kappa = 1.3$.

8. **Equation (8) · Constraint C4 (Tie-Breaking Equality):**
   $$x_i = x_j, \quad \forall i, j \text{ such that } w_i = w_j$$
   Eliminates arbitrary solver choices between courses with identical objective weights.

9. **Equation (9) · Constraint C5 (Non-Negativity):**
   $$x_i \ge 0, \quad \forall i \quad (\text{implied by C2})$$

10. **Equation (10) · Sensitivity and Shadow Price:**
    $$\lambda = 3.0$$
    The shadow price represents the dual marginal value of relaxing the budget constraint by one unit. One extra hour directed optimally yields 3.0 units of the constructed optimisation objective, allocated to unconstrained courses with weight 3.0 (Real Analysis, Complex Analysis, PDEs).

11. **Model C (Piecewise-Linear Diminishing Returns, added extension):**
    Splits time above the minimum floor $L_i$ into $K=3$ segments: $\ell = (60, 60, \infty)$ minutes, with decreasing valuation factors $\phi = (1.0, 0.6, 0.3)$.
    Variables: $s_{ik} \in [0, \ell_k]$, where $x_i = L_i + \sum_k s_{ik}$.
    Objective:
    $$\max Z_C = \sum_i \sum_k w_i \cdot \phi_k \cdot s_{ik} \quad (w_i = c_i d_i p_i)$$
    Subject to total budget C1, minimum coverage C2, user constraints, and tie-breaking C4. Proportional cap C3 is optional/disabled by default.

---

## (b) The Case-Study Numbers

- **Population & Sample:**
  - Total eligible cohort: 200 third-year students (sessions 2021-22 and 2022-23; author excluded to ensure neutrality from $N=201$).
  - Respondents: $n = 147$ (73.5% response rate).
  - Breakdown:
    - Less than 30 min: 7 (4.8%), midpoint 0.25 h/day
    - 30 min to 1 hr: 38 (25.9%), midpoint 0.75 h/day
    - 2 to 3 hrs: 31 (21.1%), midpoint 2.5 h/day
    - 4 hrs or above: 11 (7.5%), verified midpoint $52/11 \approx 4.7273$ h/day (2 at 6h, 4 at 5h, 5 at 4h)
    - Only before exams: 60 (40.8%), assigned 0.0 h/day
    - Mean: 1.087 h/day $\times 7 = 7.6$ h/week = 456 min/week.

- **Curriculum and Course Allocations:**
  Total 10 desk-study courses (Math 311 Sessional and Math 312 Viva Voce excluded as attendance/oral based):
  1. Real Analysis (II): $c=3, d=1.0 \implies w_A=3, w_B=3.0$
  2. Complex Analysis (I): $c=3, d=1.0 \implies w_A=3, w_B=3.0$
  3. Abstract Algebra: $c=4, d=1.2 \implies w_A=4, w_B=4.8$
  4. Partial Differential Equations: $c=3, d=1.0 \implies w_A=3, w_B=3.0$
  5. Methods of Applied Mathematics: $c=4, d=1.1 \implies w_A=4, w_B=4.4$
  6. Mechanics: $c=4, d=1.2 \implies w_A=4, w_B=4.8$
  7. Numerical Analysis (I): $c=3, d=0.8 \implies w_A=3, w_B=2.4$
  8. Linear Programming: $c=4, d=0.8 \implies w_A=4, w_B=3.2$
  9. Number Theory: $c=3, d=0.9 \implies w_A=3, w_B=2.7$
  10. Mathematical Computing Lab: $c=3, d=0.8 \implies w_A=3, w_B=2.4$

- **Exact HiGHS Solutions vs. Printed Paper Table 3:**
  - **Total budget:** 456.0 min (7 h 36 m).
  - **Model A exact allocations:**
    - Four 4-credit courses at proportional cap: $4 / 34 \times 456 \times 1.3 \approx 69.7412$ min ($\approx 69.7$ min).
    - Six 3-credit courses get remaining time: $(456 - 4 \times 69.7412)/6 \approx 29.5059$ min ($\approx 29.5$ min).
    - Sum: exactly 456.0 min.
    - Paper Table 3 printed: 30 min (3-credit courses), 1 h 10 m (4-credit courses).
  - **Model B exact allocations:**
    - Total weight: 33.7.
    - Proportional cap factor: $456 \times 1.3 / 33.7 \approx 17.5905$ min per unit weight.
    - Abstract Algebra & Mechanics ($w=4.8$): cap is $84.4344$ min. Both hit cap ($\approx 84.4$ min).
    - Methods of Applied Mathematics ($w=4.4$): cap is $77.3982$ min. Hits cap ($\approx 77.4$ min).
    - Linear Programming ($w=3.2$): cap is $56.2896$ min. Hits cap ($\approx 56.3$ min).
    - Numerical Analysis, Number Theory, Computing Lab ($w=2.4, 2.7, 2.4$): all 3 hit floor $L_i = 20.0$ min.
    - Real Analysis, Complex Analysis, PDEs ($w=3.0$): cap is $52.77$ min. They share the residual budget: $(456 - 84.4344\times 2 - 77.3982 - 56.2896 - 60)/3 = 93.4433 / 3 = 31.1478$ min ($\approx 31.1$ min).
    - Sum: exactly 456.0 min.
    - Paper Table 3 printed: 31 min, 31 min, 1 h 24 m, 31 min, 1 h 17 m, 1 h 24 m, 20 min, 56 min, 20 min, 20 min.
  - **Shadow Price:** $\lambda = 3.0$ per hour for both Model A and Model B.

---

## (c) Layout Followed from the Image and Specifications, Section by Section

While `demo-ui.png` provides the blueprint for information density, strict tabular alignment, compact metrics, and uppercase mono sub-headers, all styling rules (square corners, no drop shadows, no gradients, hairline rules, `#CC3300` vermilion accent, Inter and JetBrains Mono) are governed by the Swiss design system (`02_SWISS_DESIGN_SYSTEM.md`).

Section order:
- **00 Masthead:**
  - Height 64px, 1px bottom rule.
  - Left: `STUDY BUDGET` in mono label style.
  - Center: Navigation anchor links (`Calculator`, `Method`, `Case study`, `About`, `Source`).
  - Right: Unit toggle `MIN | H` (two adjoining sharp rectangles, active state filled ink `#111111` with paper `#F5F3EE` text).
- **01 Intro:**
  - Asymmetrical editorial layout across 12 columns.
  - Columns 1–8: High-impact display statement (`Split your study hours across your courses and see the arithmetic.`) and body text defining limits honestly.
  - Columns 9–12: Numbered flow (`1 Enter courses and hours · 2 Add your own rules · 3 Compare the three models`) and quick jump links (`Go to the calculator ↓`, `Load the case study`).
- **02 Calculator:**
  - **Stage A · Plan:**
    - Left (cols 1–4): Multimodal drag-and-drop parse panel (text, screenshot, PDF, DOCX, voice audio) with status warnings and questions.
    - Right (cols 5–12): High-density course input table with tabular headers (`COURSE`, `CREDITS`, `DIFFICULTY`, `MIN`, `MAX`, `LOCK`, actions).
    - Segmented 5-level difficulty controls (`Most difficult 1.2` down to `Easiest 0.8`).
    - Budget configuration (Weekly, Daily with days/week, Custom periods).
  - **Stage B · Rules:**
    - Plain-language constraint builder with interactive sentence previews (`At least 45 min for Calculus.`).
    - Rule toggles, delete actions, and real-time infeasibility warnings.
  - **Stage C · Results:**
    - Summary metrics bar: Total time, Shadow price, Binding constraints.
    - 7+5 Column split on desktop: Allocation Table (left) + Horizontal Grouped Bar Chart (right with direct labels and minimum floor marker).
    - "Why they differ" auto-generated causal explanations.
    - Constraint status table (binding status and minute slacks).
    - Shadow price sensitivity card with numeric +30 min check.
    - Export action row (CSV, PDF, ICS).
- **03 Method:**
  - 2-Column editorial presentation.
  - Left: Clear mathematical explanation in the author's voice.
  - Right: Distinctive formula cards in `--paper-2` `#ECE9E1` with 1px border.
- **04 Case Study Drawer:**
  - Collapsible full-width row with `+` / `−` indicator.
  - Survey methodology and Table 1 respondent breakdown.
  - Printed Table 3 reproduction alongside calculated exact comparison.
  - Prominent primary action: `Load case study into calculator`.
- **05 About:**
  - Editorial author biography of Md. Ali Arman Rafi, University of Chittagong.
  - Structured facts list in mono: Department, Institution, Session, Paper date, GitHub link, Email.
- **06 Footer:**
  - Repository link, author contact, and explicit memory-only privacy notice.

---

## (d) Inconsistencies and Discrepancies in the Research Paper

1. **Table 3 Sum Inconsistency Due to Integer Rounding:**
   - In the paper's Table 3, individual course allocations are printed in rounded whole minutes or hours.
   - For Model A, summing the printed entries gives:
     $$30 + 30 + 70 + 30 + 70 + 70 + 30 + 70 + 30 + 30 = 460\text{ min} = 7\text{ h } 40\text{ m}$$
   - For Model B, summing the printed entries gives:
     $$31 + 31 + 84 + 31 + 77 + 84 + 20 + 56 + 20 + 20 = 454\text{ min} = 7\text{ h } 34\text{ m}$$
   - Both columns state "Total: 7 h 36 m" (456 min) at the bottom. The exact LP solutions indeed sum to 456.0 min. The drawer and results explicitly note this rounding discrepancy honestly.

2. **Omission of Capped Courses in Section 4.1:**
   - In Section 4.1 (Sensitivity Analysis and the Shadow Price), the paper writes:
     > *"In the Improved solution, Abstract Algebra and Mechanics have both reached their proportional upper bounds."*
   - However, solving the exact Model B LP reveals that **four** courses hit their proportional upper bounds:
     - Abstract Algebra ($w=4.8$, allocated $84.43$ min, cap $84.43$ min)
     - Mechanics ($w=4.8$, allocated $84.43$ min, cap $84.43$ min)
     - Methods of Applied Mathematics ($w=4.4$, allocated $77.40$ min, cap $77.40$ min)
     - Linear Programming ($w=3.2$, allocated $56.29$ min, cap $56.29$ min)
   - The paper mentions only the top two ($w=4.8$), but Applied Math and Linear Programming are strictly binding against their caps as well. The tool's constraint report accurately reports all four binding caps.

3. **Population and Cohort Sizing:**
   - On page 1 and page 3, the population of the two cohorts is given as $N = 201$. The author did not participate to preserve neutrality, leaving $200$ eligible students, of which $n = 147$ responded (73.5%).
   - The budget calculation $159.75 / 147 \times 7 = 7.6071$ hours, rounded to 7.6 h (456 minutes).
