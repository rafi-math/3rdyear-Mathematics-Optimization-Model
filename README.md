# Deterministic Academic Resource Optimization
### Department of Mathematics, University of Chittagong

## 1. Project Overview
This project applies **Linear Programming (LP)** to solve a real-world resource allocation problem: maximizing academic performance across a 1000-mark syllabus. By treating the credit-weighted courses as variables, the model calculates the most efficient study schedule under temporal and cognitive constraints.

## 2. Mathematical Formulation
To prove the core mathematics, the model is defined as:
* **Objective Function:** Maximize $Z = \sum_{i=1}^{12} (Marks_i \times Hours_i)$
* **Total Time Constraint:** $\sum Hours_i \leq 48$ hours/week
* **Boundary Constraints:** $2 \leq Hours_i \leq 7$ (Prevents over-allocation and burnout).

## 3. Technology Stack
* **Language:** Python 3.x
* **Library:** PuLP (Optimization Ver. 2.9)
* **Solver:** CBC (Coin-or branch and cut)

## 4. Course Distribution (Data Source)
Based on the official B.Sc. (Hon's) 3rd Year curriculum (Year of Examination 2024 & 2025), including:
- Abstract Algebra (100 Marks)
- Linear Programming (100 Marks)
- Methods of Applied Mathematics (100 Marks)
- Mechanics (100 Marks)
- ... and 8 other core modules.
