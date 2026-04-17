from pulp import *

# 1. Initialize the Optimization Problem
model = LpProblem("CU_Mathematics_Department_Optimization", LpMaximize)

# 2. Exact Data from University of Chittagong 3rd Year Syllabus
# Format: "Course Title": [Marks, Credits]
syllabus = {
    "Real Analysis( II)": [75, 3],
    "Complex Analysis( I)": [75, 3],
    "Abstract Algebra": [100, 4],
    "Partial Differential equations": [75, 3],
    "Methods of Applied Mathematics": [100, 4],
    "Mechanics": [100, 4],
    "Numerical Analysis (I)": [75, 3],
    "Linear Programming": [100, 4],
    "Number Theory": [75, 3],
    "Mathematical Computing Lab": [75, 3],
    "Sessional (Tutorial+ Attendance)": [75, 3],
    "Viva Voce": [75, 3]
}

# 3. Variables: Hours to spend per week on each
h = LpVariable.dicts("Study_Hrs", syllabus.keys(), lowBound=0, cat='Continuous')

# 4. Objective Function: Maximize (Marks * Hours)
model += lpSum([syllabus[c][0] * h[c] for c in syllabus.keys()])

# 5. Constraints
# Rule 1: Total weekly study time (e.g., 48 hours)
model += lpSum([h[c] for c in syllabus.keys()]) <= 48

# Rule 2: Balanced Allocation (Realistic Study)
for c in syllabus.keys():
    # Minimum requirement: 2 hours for all, 1 for Viva/Sessional
    if "Viva" in c or "Sessional" in c:
        model += h[c] >= 1
    else:
        model += h[c] >= 2

    # Maximum Limit: No more than 7 hours per subject to prevent burnout
    model += h[c] <= 7

# 6. Solve using the Simplex Algorithm
model.solve()

# 7. Final Output Presentation
print(f"{'OFFICIAL COURSE TITLE':<35} | {'OPTIMIZED HOURS/WEEK'}")
print("-" * 65)
for c in syllabus.keys():
    print(f"{c:<35} | {h[c].varValue:>10.2f} hours")