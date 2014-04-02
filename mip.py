"""
Formulate and solve orienteering problem for a given NetworkX graph.
"""
import time
import networkx as nx
import pylab as plt
import pulp as pl

DEBUG = True

NODE_COLOR_NORMAL = '#5555EE'
NODE_BORDER_COLOR_NORMAL = '0.2'
NODE_COLOR_PATH = '#009926'
NODE_BORDER_COLOR_PATH = '0.2'
NODE_SIZE_NORMAL = 60
LABEL_COLOR_NORMAL = '0.9'
LABEL_FONT_SIZE_NORMAL = 11
EDGE_COLOR_NORMAL = '0.2'
EDGE_WIDTH_NORMAL = 2.0
EDGE_COLOR_PATH = '#009926'
EDGE_WIDTH_PATH = 3.0

def find_path(g, start, end, budget, maxnodes=10, dry=False):
    if start != end:
        return find_path_aux(g, start, end, budget, maxnodes, dry)
    else:
        startedges = g.edges(start, data=True)
        dummy = g.number_of_nodes() + 1
        g.add_node(dummy, w=0)
        for (u, v, d) in startedges:
            assert u == start
            g.add_edge(v, dummy, t=d['t'])
        (solstatus, obj, path) = find_path_aux(g, start, dummy,
                                               budget, maxnodes, dry)
        g.remove_node(dummy)
        if path != None:
            assert path[-1] == dummy
            path[-1] = start
        return (solstatus, obj, path)


def find_path_aux(g, start, end, budget, maxnodes, dry=False):
    # Problem parameters
    N = g.number_of_nodes()
    S = start
    T = end
    B = budget
    M = maxnodes

    if DEBUG:
        print '(N, S, T, B, M) =', ','.join(map(str, [N, S, T, B, M]))

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
    # No edges "entering" S or "leaving" T
    for i in range(1, N+1):
        problem += x[i][S] == 0
        problem += x[T][i] == 0
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
    # Vertex budget constraint (experimental)
    problem += pl.lpSum([x[i][j]
                        for i in range(1, N+1)
                        for j in range(1, N+1)]) <= M
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
    # NOTE: Constant term in the objective is omitted.
    stime = time.time()
    problem.writeLP("mip.lp")
    etime = time.time()
    if DEBUG:
        print 'Time to write to file:', etime - stime
    if dry == True:
        return (None, None, None)
    
    # Solve
    stime = time.time()
    status = problem.solve(pl.solvers.GUROBI())
    etime = time.time()
    if DEBUG:
        print 'Time to solve:', etime - stime

    # Print solution status and objective
    solstatus = pl.LpStatus[status]
    # If optimal plot path in graph
    if solstatus != 'Optimal':
        obj = None
        path = None
    else:
        obj = pl.value(problem.objective)
        nxt = dict()
        for i in range(1, N+1):
            for j in range(1, N+1):
                #if DEBUG:
                #    print x[i][j], pl.value(x[i][j])
                if pl.value(x[i][j]) == 1:
                    nxt[i] = j
        path = [S]
        v = S
        while v != T:
            v = nxt[v]
            path.append(v)
    return (solstatus, obj, path)

def plot_path(g, path, pos=None):
    # Create edgelist of path
    if path == None:
        edgelist = []
    else:
        edgelist = zip(path[:-1], path[1:])
    # Plot graph
    if pos == None:
        pos = nx.graphviz_layout(g)
    nodes = nx.draw_networkx_nodes(g,
                                   pos,
                                   node_size=NODE_SIZE_NORMAL,
                                   node_color=NODE_COLOR_NORMAL)
    nodes.set_edgecolor(NODE_BORDER_COLOR_NORMAL)
#    nx.draw_networkx_labels(g,
#                            pos,
#                            font_color=LABEL_COLOR_NORMAL,
#                            font_size=LABEL_FONT_SIZE_NORMAL)
    nx.draw_networkx_edges(g,
                           pos,
                           width=EDGE_WIDTH_NORMAL,
                           edge_color=EDGE_COLOR_NORMAL)
    if path == None or path == []:
        plt.show()
        return
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

# Example graphs
def demo_graph_small():
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
    return g

def demo_graph_gnp(n=30):
    g = nx.gnp_random_graph(n+1, 0.2)
    g.remove_node(0)
    for u, v, d in g.edges_iter(data=True):
        d['t'] = 1
    for u, d in g.nodes_iter(data=True):
        d['w'] = 1
    return g

if __name__ == '__main__':
    g = demo_graph_gnp(n=150)
    (status, objective, path) = find_path(g, start=1, end=1,
                                          budget=30, maxnodes=10)
    print 'Status: ', status
    print 'Objective = ', objective
    plot_path(g, path)
