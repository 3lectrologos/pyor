"""
Formulate and solve orienteering problem for an example NetworkX graph.
"""
import networkx as nx
import pylab as plt
import pulp as pl

DEBUG = False

NODE_COLOR_NORMAL = '#5555EE'
NODE_BORDER_COLOR_NORMAL = '0.2'
NODE_COLOR_PATH = '#009926'
NODE_BORDER_COLOR_PATH = '0.2'
NODE_SIZE_NORMAL = 600
LABEL_COLOR_NORMAL = '0.9'
LABEL_FONT_SIZE_NORMAL = 11
EDGE_COLOR_NORMAL = '0.2'
EDGE_WIDTH_NORMAL = 2.0
EDGE_COLOR_PATH = '#009926'
EDGE_WIDTH_PATH = 3.0

# Graph set-up
g = nx.Graph()
g.add_node(1, w=0)
g.add_node(2, w=1.5)
g.add_node(3, w=3)
g.add_node(4, w=1)
g.add_node(5, w=0)

g.add_edge(1, 2, t=1)
g.add_edge(1, 3, t=1)
g.add_edge(1, 5, t=1)
g.add_edge(2, 4, t=1)
g.add_edge(2, 5, t=1)
g.add_edge(3, 5, t=1)

# Problem parameters
N = g.number_of_nodes()
S = 3
T = 4
B = 3

# Problem init
problem = pl.LpProblem("Orienteering", pl.LpMaximize)
# Variables
x = pl.LpVariable.dicts("x", (range(1, N+1), range(1, N+1)), cat="Binary")
u = pl.LpVariable.dicts("u", range(1, N+1), cat="Integer")
# Read edge weights and set constraints for non-existing edges
t = dict()
for i in range(1, N+1):
    t[i] = dict()
    for j in range(1, N+1):
        try:
            t[i][j] = g.edge[i][j]['t']
        except KeyError:
            # Value doesn't matter in this case, since we
            # explicitly set x[i][j] = 0
            t[i][j] = 1
            problem += x[i][j] == 0
# Read node weights
w = dict()
for i in range(1, N+1):
    try:
        w[i] = g.node[i]['w']
    except KeyError:
        w[i] = 0
# Objective
problem += w[S] + w[T] + pl.lpSum([w[i]*x[i][j] for i in range(1, N+1) if i != S
                                                for j in range(1, N+1)])
# Path starts at S and ends at T
problem += pl.lpSum([x[S][j] for j in range(1, N+1)]) == 1
problem += pl.lpSum([x[i][T] for i in range(1, N+1)]) == 1
# "Flow conservation" constraints
for k in range(1, N+1):
    if k != S and k != T:
        problem += pl.lpSum([x[i][k] for i in range(1, N+1)]) <= 1
        problem += pl.lpSum([x[k][j] for j in range(1, N+1)]) <= 1
        problem += pl.lpSum([x[i][k] for i in range(1, N+1) if i != T] +
                            [-x[k][j] for j in range(1, N+1) if j != S]) == 0
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
print 'Solution status:', pl.LpStatus[status]
# If optimal plot path in graph
print 'Objective =', pl.value(problem.objective)
if status == 1:
    nxt = dict()
    for i in range(1, N+1):
        for j in range(1, N+1):
            if DEBUG:
                print x[i][j], pl.value(x[i][j])
            if pl.value(x[i][j]) == 1:
                nxt[i] = j
    path = [S]
    edgelist = []
    v = S
    while True:
        path.append(nxt[v])
        edgelist.append((v, nxt[v]))
        v = nxt[v]
        if v == T:
            break
    pos = nx.graphviz_layout(g)
    nodes = nx.draw_networkx_nodes(g,
                                   pos,
                                   node_size=NODE_SIZE_NORMAL,
                                   node_color=NODE_COLOR_NORMAL)
    nodes.set_edgecolor(NODE_BORDER_COLOR_NORMAL)
    nx.draw_networkx_labels(g,
                            pos,
                            font_color=LABEL_COLOR_NORMAL,
                            font_size=LABEL_FONT_SIZE_NORMAL)
    nx.draw_networkx_edges(g,
                           pos,
                           width=EDGE_WIDTH_NORMAL,
                           edge_color=EDGE_COLOR_NORMAL)
    nodes = nx.draw_networkx_nodes(g,
                                   pos,
                                   nodelist=path,
                                   node_size=NODE_SIZE_NORMAL,
                                   node_color=NODE_COLOR_PATH)
    nodes.set_edgecolor(NODE_BORDER_COLOR_PATH)
    nx.draw_networkx_edges(g,
                           pos,
                           edgelist=edgelist,
                           width=EDGE_WIDTH_PATH,
                           edge_color=EDGE_COLOR_PATH)
    plt.show()
