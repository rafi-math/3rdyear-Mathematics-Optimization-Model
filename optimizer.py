from pulp import *

# 1. Setup the Maximization Problem
model = LpProblem("CU_Math_Optimization", LpMaximize)

# 2. Official Syllabus Data (Course: [Max Marks, Credits])
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

# 3. Create Decision Variables
h = LpVariable.dicts("Hrs", syllabus.keys(), lowBound=0)

# 4. Define Objective Function
model += lpSum([syllabus[c][0] * h[c] for c in syllabus.keys()])

# 5. Define Constraints
model += lpSum([h[c] for c in syllabus.keys()]) <= 48  # Total hours limit

for c in syllabus.keys():
    # Minimum 2 hours for theory, 1 for viva
    if "Viva" in c or "Sessional" in c:
        model += h[c] >= 1
    else:
        model += h[c] >= 2

    # Maximum 7 hours to ensure balance
    model += h[c] <= 7

# 6. Solve and Print
model.solve()
print(f"{'COURSE':<35} | {'HOURS'}")
print("-" * 45)
for c in syllabus.keys():
    print(f"{c:<35} | {h[c].varValue:>5.2f}")