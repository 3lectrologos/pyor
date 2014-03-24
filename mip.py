import networkx as nx
import pulp as pl

# Problem parameters
S = 3
T = 4
N = 5
B = 100
# Edge weights
t = dict()
for i in range(1, N+1):
    t[i] = dict()
    for j in range(1, N+1):
        t[i][j] = 1
# Vertex weights
w = dict()
w[1] = 0
w[2] = 1.5
w[3] = 3
w[4] = 1
w[5] = 0

# Problem init
problem = pl.LpProblem("Orienteering", pl.LpMaximize)
# Variables
x = pl.LpVariable.dicts("x", (range(1, N+1), range(1, N+1)), cat="Binary")
u = pl.LpVariable.dicts("u", range(1, N+1), cat="Integer")
# Objective
problem += pl.lpSum([w[i]*x[i][j] for i in range(1, N+1) for j in range(1, N+1)])
# Path starts at S and ends at T
problem += pl.lpSum([x[S][j] for j in range(1, N+1)]) == 1
problem += pl.lpSum([x[i][T] for i in range(1, N+1)]) == 1
# Explicit constraints for non-existing edges (including loops)
for i in range(1, N+1):
    problem += x[i][i] == 0
problem += x[2][3] == 0
problem += x[3][2] == 0
problem += x[1][4] == 0
problem += x[4][1] == 0
problem += x[3][4] == 0
problem += x[4][3] == 0
problem += x[4][5] == 0
problem += x[5][4] == 0
# "Flow conservation" constraints
for k in range(1, N+1):
    if k != S and k != T:
        problem += pl.lpSum([x[i][k] for i in range(1, N+1)]) <= 1
        problem += pl.lpSum([x[k][j] for j in range(1, N+1)]) <= 1
        problem += pl.lpSum([x[i][k] for i in range(1, N+1)] +
                            [-x[k][j] for j in range(1, N+1)]) == 0
# Edge budget constraint
problem += pl.lpSum([t[i][j]*x[i][j]
                     for i in range(1, N+1)
                     for j in range(1, N+1)]) <= B
# Subtour elimination constraints (1)
for k in range(1, N+1):
    if k != S:
        problem += u[k] >= 2
        problem += u[k] <= N
problem += u[S] == 1
# Subtour elimination constraints (2)
for i in range(1, N+1):
    for j in range(1, N+1):
        if i != S and j != S:
            problem += u[i] - u[j] + (N-1)*x[i][j] <= N-2
# Write problem to lp file
problem.writeLP("mip.lp")
# Solve
status = problem.solve()
# Print solution
print pl.LpStatus[status]
print 'obj =', pl.value(problem.objective)
for i in range(1, N+1):
    for j in range(1, N+1):
        print x[i][j], pl.value(x[i][j])
