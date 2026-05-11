import pulp as pl
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from collections import Counter
from itertools import combinations


COURSE_MAP = {
    1:  ("Math 301 - Real Analysis (II)",               [75, 3]),
    2:  ("Math 302 - Complex Analysis (I)",             [75, 3]),
    3:  ("Math 303 - Abstract Algebra",                 [100, 4]),
    4:  ("Math 304 - Partial Differential Equations",   [75, 3]),
    5:  ("Math 305 - Methods of Applied Mathematics",   [100, 4]),
    6:  ("Math 306 - Mechanics",                        [100, 4]),
    7:  ("Math 307 - Numerical Analysis (I)",           [75, 3]),
    8:  ("Math 308 - Linear Programming",               [100, 4]),
    9:  ("Math 309 - Number Theory",                    [75, 3]),
    10: ("Math 310 - Mathematical Computing Lab",       [75, 3]),
}

COURSE_NAMES = {n: name for n, (name, _) in COURSE_MAP.items()}

COURSE_SHORT = {
    1:  "Real Analysis (II)",
    2:  "Complex Analysis (I)",
    3:  "Abstract Algebra",
    4:  "Partial Differential Equations",
    5:  "Methods of Applied Mathematics",
    6:  "Mechanics",
    7:  "Numerical Analysis (I)",
    8:  "Linear Programming",
    9:  "Number Theory",
    10: "Mathematical Computing Lab",
}

SYLLABUS = {name: data for _, (name, data) in COURSE_MAP.items()}

DIFF_LEVELS = [
    (1.2, "Most Difficult"),
    (1.1, "Difficult"),
    (1.0, "Medium"),
    (0.9, "Easy"),
    (0.8, "Easiest"),
]

LEVEL_LABEL = {d: lbl for d, lbl in DIFF_LEVELS}


RESPONSES = [
    "Less than 30 minutes", "30 minutes to 1 hour", "Only before exams",
    "30 minutes to 1 hour", "Only before exams", "30 minutes to 1 hour",
    "2 to 3 hours", "Only before exams", "4 hours or above", "4 hours or above",
    "30 minutes to 1 hour", "2 to 3 hours", "2 to 3 hours", "Only before exams",
    "30 minutes to 1 hour", "Only before exams", "4 hours or above", "Only before exams",
    "2 to 3 hours", "Only before exams", "2 to 3 hours", "2 to 3 hours",
    "Only before exams", "30 minutes to 1 hour", "30 minutes to 1 hour",
    "2 to 3 hours", "Only before exams", "2 to 3 hours", "30 minutes to 1 hour",
    "30 minutes to 1 hour", "Only before exams", "2 to 3 hours", "4 hours or above",
    "Only before exams", "Only before exams", "2 to 3 hours", "2 to 3 hours",
    "30 minutes to 1 hour", "2 to 3 hours", "30 minutes to 1 hour", "Only before exams",
    "30 minutes to 1 hour", "Only before exams", "Only before exams", "2 to 3 hours",
    "Only before exams", "Only before exams", "4 hours or above", "2 to 3 hours",
    "Only before exams", "30 minutes to 1 hour", "Only before exams",
    "30 minutes to 1 hour", "Only before exams", "Only before exams",
    "4 hours or above", "2 to 3 hours", "Only before exams", "Only before exams",
    "30 minutes to 1 hour", "Only before exams", "Only before exams",
    "Only before exams", "Only before exams", "Only before exams",
    "30 minutes to 1 hour", "30 minutes to 1 hour", "2 to 3 hours",
    "30 minutes to 1 hour", "2 to 3 hours", "30 minutes to 1 hour",
    "30 minutes to 1 hour", "Only before exams", "Only before exams",
    "2 to 3 hours", "4 hours or above", "Only before exams", "2 to 3 hours",
    "30 minutes to 1 hour", "30 minutes to 1 hour", "30 minutes to 1 hour",
    "Only before exams", "Only before exams", "2 to 3 hours", "2 to 3 hours",
    "Only before exams", "30 minutes to 1 hour", "Less than 30 minutes",
    "Only before exams", "2 to 3 hours", "4 hours or above", "Only before exams",
    "Only before exams", "Only before exams", "2 to 3 hours", "30 minutes to 1 hour",
    "2 to 3 hours", "2 to 3 hours", "2 to 3 hours", "Only before exams",
    "Only before exams", "Only before exams", "30 minutes to 1 hour",
    "Less than 30 minutes", "30 minutes to 1 hour", "Only before exams",
    "30 minutes to 1 hour", "30 minutes to 1 hour", "Less than 30 minutes",
    "30 minutes to 1 hour", "Only before exams", "Less than 30 minutes",
    "30 minutes to 1 hour", "Only before exams", "Only before exams",
    "30 minutes to 1 hour", "30 minutes to 1 hour", "2 to 3 hours",
    "Less than 30 minutes", "Only before exams", "4 hours or above",
    "Only before exams", "4 hours or above", "Only before exams", "Only before exams",
    "2 to 3 hours", "30 minutes to 1 hour", "Only before exams", "2 to 3 hours",
    "Only before exams", "4 hours or above", "Only before exams", "Only before exams",
    "Only before exams", "Only before exams", "Only before exams",
    "30 minutes to 1 hour", "Only before exams", "2 to 3 hours", "Only before exams",
    "30 minutes to 1 hour", "Only before exams", "30 minutes to 1 hour",
    "Less than 30 minutes", "2 to 3 hours", "30 minutes to 1 hour", "Only before exams"
]


FOLLOWUP_MIDPOINT = (2*6 + 4*5 + 5*4) / 11

CAT_ORDER = [
    ("Less than 30 minutes", 0.25),
    ("30 minutes to 1 hour", 0.75),
    ("2 to 3 hours", 2.50),
    ("4 hours or above", FOLLOWUP_MIDPOINT),
    ("Only before exams", 0.00),
]

SHORT_LABELS = [
    "< 30 min",
    "30 min–1 hr",
    "2–3 hrs",
    "4 hrs or above\n(corrected: 4.73h)",
    "Only before exams",
]


counts = Counter(RESPONSES)

N = 147
N_TOTAL = 200

freq = [counts[lbl] for lbl, _ in CAT_ORDER]
pcts = [f / N * 100 for f in freq]

avg_daily = sum(counts[lbl] * mid for lbl, mid in CAT_ORDER) / N
avg_weekly = avg_daily * 7

LP_BUDGET = round(avg_weekly, 1)

MIN_HRS = 1 / 3
SCALE = 1.3


def mins_to_label(h):
    total_min = round(h * 60)

    hrs = total_min // 60
    mins = total_min % 60

    if hrs > 0 and mins > 0:
        return f"{hrs}h {mins}m"

    if hrs > 0:
        return f"{hrs}h"

    return f"{mins}m"


def mins_to_long(h):
    total_min = round(h * 60)

    hrs = total_min // 60
    mins = total_min % 60

    if hrs > 0 and mins > 0:
        h_word = "hour" if hrs == 1 else "hours"
        m_word = "min" if mins == 1 else "mins"
        return f"{h:.3f}h ({hrs} {h_word} {mins} {m_word})"

    if hrs > 0:
        h_word = "hour" if hrs == 1 else "hours"
        return f"{h:.3f}h ({hrs} {h_word})"

    m_word = "min" if total_min == 1 else "mins"
    return f"{h:.3f}h ({total_min} {m_word})"


def parse_input(raw, already):
    nums = []

    if not raw.strip():
        return [], None

    for part in raw.strip().split(","):
        part = part.strip()

        if not part:
            continue

        try:
            n = int(part)

        except ValueError:
            return None, f"'{part}' is not a number."

        if not 1 <= n <= 10:
            return None, f"{n} out of range."

        if n in already:
            return None, f"{COURSE_SHORT[n]} already assigned."

        nums.append(n)

    return nums, None


def compute_proportional_max(weights):
    total_w = sum(weights.values())

    return {
        c: max(
            MIN_HRS,
            min(
                LP_BUDGET,
                (weights[c] / total_w) * LP_BUDGET * SCALE
            )
        )
        for c in weights
    }


def solve_lp(weights, label="Model"):
    mdl = pl.LpProblem(label.replace(" ", "_"), pl.LpMaximize)

    h = pl.LpVariable.dicts(
        "h",
        SYLLABUS.keys(),
        lowBound=0
    )

    max_hrs = compute_proportional_max(weights)

    mdl += pl.lpSum(weights[c] * h[c] for c in SYLLABUS)

    mdl += pl.lpSum(h[c] for c in SYLLABUS) <= LP_BUDGET

    for c in SYLLABUS:
        mdl += h[c] >= MIN_HRS
        mdl += h[c] <= max_hrs[c]

    courses = list(SYLLABUS.keys())

    for i, j in combinations(range(len(courses)), 2):
        ci, cj = courses[i], courses[j]

        if abs(weights[ci] - weights[cj]) < 1e-9:
            mdl += h[ci] == h[cj]

    mdl.solve(pl.PULP_CBC_CMD(msg=0))

    alloc = {
        c: round(h[c].varValue, 6)
        for c in SYLLABUS
    }

    obj = round(pl.value(mdl.objective), 4)

    shadow = round(
        mdl.constraints[list(mdl.constraints.keys())[0]].pi,
        4
    )

    return alloc, obj, shadow


print("\nSurvey data:\n")

print(
    f"Respondents : {N}/{N_TOTAL} "
    f"({N/N_TOTAL*100:.1f}%)"
)

print()

print(f"{'Category':<30} {'n':>4} {'%':>6} {'Midpoint':>10}")

for (lbl, mid), f, p in zip(CAT_ORDER, freq, pcts):

    note = ""

    if lbl == "4 hours or above":
        note = " <- corrected"

    print(
        f"{lbl:<30} "
        f"{f:>4} "
        f"{p:>5.1f}% "
        f"{mid:>8.2f}h{note}"
    )

print()

print(f"Weighted avg daily  : {avg_daily:.2f} h/day")
print(f"Weighted avg weekly : {avg_weekly:.2f} h/week")

print(
    f"LP budget : {LP_BUDGET} h/week "
    f"({int(LP_BUDGET)}h "
    f"{round((LP_BUDGET % 1) * 60)}min)"
)


colors = ["#2E86AB", "#457B9D", "#1D3557", "#0D1B2A", "#E63946"]

fig, axes = plt.subplots(1, 2, figsize=(13, 5.5))

fig.patch.set_facecolor("white")


ax1 = axes[0]

y_pos = range(len(SHORT_LABELS))

bars = ax1.barh(
    list(y_pos),
    pcts,
    color=colors,
    edgecolor="white",
    linewidth=0.9,
    height=0.55
)

ax1.invert_yaxis()

ax1.set_yticks(list(y_pos))
ax1.set_yticklabels(SHORT_LABELS, fontsize=9.5)

ax1.set_xlabel("Percentage of Respondents (%)", fontsize=10)

ax1.set_xlim(0, 55)

ax1.set_title(
    "Daily Self-Study Habits\nof Mathematics Students",
    fontsize=10.5,
    fontweight="bold"
)

ax1.spines[["top", "right"]].set_visible(False)

for bar, f, p in zip(bars, freq, pcts):

    ax1.text(
        p + 0.6,
        bar.get_y() + bar.get_height()/2,
        f"{f} ({p:.1f}%)",
        va="center",
        ha="left",
        fontsize=8.8
    )


ax2 = axes[1]

explode = (0, 0, 0, 0, 0.06)

wedges, texts, autotexts = ax2.pie(
    freq,
    colors=colors,
    explode=explode,
    autopct="%1.1f%%",
    startangle=130,
    pctdistance=0.75,
    wedgeprops={
        "edgecolor": "white",
        "linewidth": 1.2
    }
)

for at in autotexts:
    at.set_fontsize(8.5)
    at.set_color("white")
    at.set_fontweight("bold")


legend_patches = [
    mpatches.Patch(
        color=colors[i],
        label=f"{SHORT_LABELS[i]} (n={freq[i]})"
    )
    for i in range(len(colors))
]

ax2.legend(
    handles=legend_patches,
    loc="lower center",
    bbox_to_anchor=(0.5, -0.28),
    fontsize=8.5,
    frameon=False
)

ax2.set_title(
    "Response Distribution",
    fontsize=10.5,
    fontweight="bold"
)

plt.tight_layout(pad=2.2)

plt.savefig(
    "survey_plot.png",
    dpi=180,
    bbox_inches="tight",
    facecolor="white"
)

print("\nsurvey_plot.png saved")


print("\nDifficulty levels:\n")

for i, (d, lbl) in enumerate(DIFF_LEVELS, 1):
    print(f"{i}. {lbl:<18} d = {d}")

print("\nCourses:\n")

for num, (name, data) in COURSE_MAP.items():

    print(
        f"{num:>2}. "
        f"{COURSE_SHORT[num]:<40} "
        f"Marks={data[0]:<4} "
        f"Credits={data[1]}"
    )

print()
print("Enter course numbers separated by commas\n")

user_diff = {}
assigned = set()

for d, lbl in DIFF_LEVELS:

    while True:

        raw = input(f"{lbl} (d={d}): ").strip()

        nums, err = parse_input(raw, assigned)

        if err:
            print(err)
            continue

        assigned.update(nums)

        for n in nums:
            user_diff[COURSE_NAMES[n]] = d

        break


unassigned = sorted(set(range(1, 11)) - assigned)

if unassigned:

    print("\nAuto-assigned to easiest:\n")

    for n in unassigned:

        print(f"- {COURSE_SHORT[n]}")

        user_diff[COURSE_NAMES[n]] = 0.8


groups = {d: [] for d, _ in DIFF_LEVELS}

for num in range(1, 11):

    groups[user_diff[COURSE_NAMES[num]]].append(
        f"{num}. {COURSE_SHORT[num]}"
    )

print("\nDifficulty summary:\n")

for d, lbl in DIFF_LEVELS:

    if groups[d]:

        print(f"{lbl} (d={d})")

        for c in groups[d]:
            print(f"  - {c}")

        print()


bw = {
    name: SYLLABUS[name][1]
    for name in SYLLABUS
}

iw = {
    name: SYLLABUS[name][1] * user_diff[name]
    for name in SYLLABUS
}

print(
    f"Solving LP "
    f"(budget={LP_BUDGET}h, "
    f"min={round(MIN_HRS*60)}min)"
)

base_alloc, base_z, base_sp = solve_lp(
    bw,
    "Baseline credits only"
)

impr_alloc, impr_z, impr_sp = solve_lp(
    iw,
    "Improved credits x difficulty"
)


print("\nResults:\n")

print(
    f"{'No':>3} "
    f"{'Course':<40} "
    f"{'Cred':>5} "
    f"{'d_i':>5} "
    f"{'Level':<16} "
    f"{'Baseline':>24} "
    f"{'Improved':>24}"
)

print("-" * 125)

for num in range(1, 11):

    c = COURSE_NAMES[num]

    cr = SYLLABUS[c][1]

    d = user_diff[c]

    bv = base_alloc[c]

    iv = impr_alloc[c]

    arrow = ""

    if iv > MIN_HRS + 0.01:
        arrow = " <-"

    print(
        f"{num:>3} "
        f"{COURSE_SHORT[num]:<40} "
        f"{cr:>5} "
        f"{d:>5.1f} "
        f"{LEVEL_LABEL[d]:<16} "
        f"{mins_to_long(bv):>24} "
        f"{mins_to_long(iv):>24}{arrow}"
    )

print("-" * 125)

bt = sum(base_alloc.values())
it = sum(impr_alloc.values())

print(
    f"{'TOTAL':<56} "
    f"{mins_to_long(bt):>24} "
    f"{mins_to_long(it):>24}"
)

print()

print(f"Baseline Z = {base_z:.4f} | λ = {base_sp:.4f}")
print(f"Improved Z = {impr_z:.4f} | λ = {impr_sp:.4f}")


max_caps = compute_proportional_max(iw)

anchor = max(
    SYLLABUS.keys(),
    key=lambda c: (
        iw[c]
        if impr_alloc[c] >= max_caps[c] - 0.01
        else -999
    )
)

print(f"\nShadow price anchor : {anchor}")

print(
    f"λ = {SYLLABUS[anchor][1]} × "
    f"{user_diff[anchor]} = {impr_sp:.2f}"
)


course_labels = [
    "Real\nAnalysis",
    "Complex\nAnalysis",
    "Abstract\nAlgebra",
    "PDE",
    "Applied\nMath",
    "Mechanics",
    "Numerical\nAnalysis",
    "Linear\nProg.",
    "Number\nTheory",
    "Computing\nLab",
]

base_vals = [
    base_alloc[COURSE_NAMES[n]]
    for n in range(1, 11)
]

impr_vals = [
    impr_alloc[COURSE_NAMES[n]]
    for n in range(1, 11)
]

diff_vals = [
    user_diff[COURSE_NAMES[n]]
    for n in range(1, 11)
]


x = np.arange(len(course_labels))

w = 0.36

fig2, ax = plt.subplots(figsize=(16, 7))

fig2.patch.set_facecolor("white")

b1 = ax.bar(
    x - w/2,
    base_vals,
    w,
    label="Baseline",
    color="#A8DADC",
    edgecolor="white",
    linewidth=1
)

b2 = ax.bar(
    x + w/2,
    impr_vals,
    w,
    label="Improved",
    color="#1D3557",
    edgecolor="white",
    linewidth=1
)

for bar in b1:

    hv = bar.get_height()

    ax.text(
        bar.get_x() + bar.get_width()/2,
        hv + 0.025,
        mins_to_label(hv),
        ha="center",
        va="bottom",
        fontsize=7.5
    )

for bar in b2:

    hv = bar.get_height()

    ax.text(
        bar.get_x() + bar.get_width()/2,
        hv + 0.025,
        mins_to_label(hv),
        ha="center",
        va="bottom",
        fontsize=7.5,
        fontweight="bold"
    )

diff_short = {
    1.2: "Most\nDiff.",
    1.1: "Diff.",
    1.0: "Med.",
    0.9: "Easy",
    0.8: "Easiest",
}

for xi, (iv, dv) in enumerate(zip(impr_vals, diff_vals)):

    ax.text(
        xi + w/2,
        iv + 0.24,
        diff_short[dv],
        ha="center",
        va="bottom",
        fontsize=7,
        style="italic"
    )

ax.axhline(
    y=MIN_HRS,
    color="#E63946",
    linestyle="--",
    linewidth=1.4,
    label="Minimum floor (20 min)"
)

ax.set_xticks(x)

ax.set_xticklabels(course_labels, fontsize=9)

ax.set_ylabel("Allocated Weekly Study Hours")

ax.set_xlabel("Courses")

ax.set_title(
    "Baseline vs Improved LP Model",
    fontsize=13,
    fontweight="bold"
)

max_y = max(max(base_vals), max(impr_vals)) + 0.55

ax.set_ylim(0, max_y)

y_ticks = np.arange(0, max_y, 0.25)

ax.set_yticks(y_ticks)

ax.set_yticklabels(
    [f"{v:.2f}h ({mins_to_label(v)})" for v in y_ticks],
    fontsize=7.5
)

ax.grid(axis="y", linestyle="--", alpha=0.35)

ax.legend(frameon=False)

ax.spines["top"].set_visible(False)

ax.spines["right"].set_visible(False)

plt.tight_layout()

plt.savefig(
    "lp_plot.png",
    dpi=250,
    bbox_inches="tight",
    facecolor="white"
)

plt.show()

print("\nDone. Files saved: 3y5.png | S.png")