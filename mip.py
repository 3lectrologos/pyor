import pulp as pl

N = 5
T = 2

#-------------------------------------------------------------------------------
# Edge weights
t = dict()
for i in range(1, N+1):
    t[i] = dict()
    for j in range(1, N+1):
        t[i][j] = 1
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
# Vertex weights
w = dict()
w[1] = 0
w[2] = 1.5
w[3] = 3
w[4] = 1
w[5] = 0
#-------------------------------------------------------------------------------

u = pl.LpVariable.dicts("u", range(2, N+1), cat="Integer")
x = pl.LpVariable.dicts("x", (range(1, N+1), range(1, N+1)), cat="Binary")

problem = pl.LpProblem("Orienteering", pl.LpMaximize)
problem += pl.lpSum([w[i]*x[i][j] for i in range(2, N) for j in range(2, N+1)])

problem += pl.lpSum([x[1][j] for j in range(1, N+1)]) == 1
problem += pl.lpSum([x[i][N] for i in range(1, N+1)]) == 1

#-------------------------------------------------------------------------------
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
#-------------------------------------------------------------------------------

for k in range(2, N):
    problem += pl.lpSum([x[i][k] for i in range(1, N)]) <= 1
    problem += pl.lpSum([x[k][j] for j in range(2, N+1)]) <= 1
    problem += pl.lpSum([x[i][k] for i in range(1, N)] +
                        [-x[k][j] for j in range(2, N+1)]) == 0

problem += pl.lpSum([t[i][j]*x[i][j]
                     for i in range(1, N+1)
                     for j in range(1, N+1)]) <= T

for k in range(2, N+1):
    problem += u[k] >= 2
    problem += u[k] <= N

for i in range(2, N+1):
    for j in range(2, N+1):
        problem += u[i] - u[j] + (N-1)*x[i][j] <= N-2

problem.writeLP("mip.lp")

status = problem.solve()
print pl.LpStatus[status]

print 'obj =', pl.value(problem.objective)

for i in range(1, N+1):
    for j in range(1, N+1):
        print x[i][j], pl.value(x[i][j])
