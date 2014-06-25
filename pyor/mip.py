"""
Formulate and solve the orienteering problem for a given NetworkX graph.
"""
import os
import gurobipy as grb
import util


def find_path(g, start, end, edge_budget, node_budget, time_limit,
              verbose=True):
    if start != end:
        return find_path_aux(g, start, end,
                             edge_budget,
                             node_budget,
                             time_limit,
                             verbose)
    else:
        startedges = g.edges(start, data=True)
        dummy = g.number_of_nodes() + 1
        g.add_node(dummy, w=0)
        for (u, v, d) in startedges:
            assert u == start
            g.add_edge(v, dummy, t=d['t'])
        (solstatus, obj, path) = find_path_aux(g, start, dummy,
                                               edge_budget,
                                               node_budget,
                                               time_limit,
                                               verbose)
        g.remove_node(dummy)
        if path != None:
            assert path[-1] == dummy
            path[-1] = start
        return (solstatus, obj, path)

def find_path_aux(g, start, end, edge_budget, node_budget, time_limit,
                  verbose=True):
    # Problem parameters
    N = g.number_of_nodes()
    S = start
    T = end
    EB = edge_budget
    NB = node_budget

    grb.setParam('OutputFlag', verbose)

    if verbose:
        print '(N, S, T, EB, NB) =', ','.join(map(str, [N, S, T, EB, NB]))
    # Model init
    model = grb.Model("Orienteering")
    # Weights and variables
    w = dict()
    t = dict()
    m = dict()
    x = dict()
    u = dict()
    # Read node weights
    for i, d in g.nodes(data=True):
        u[i] = model.addVar(vtype=grb.GRB.INTEGER, name='u_'+str(i))
        try:
            w[i] = d['w']
        except KeyError:
            w[i] = 0
        try:
            m[i] = d['m']
        except KeyError:
            m[i] = 0
    # Read edge weights
    if g.is_directed():
        dg = g
    else:
        dg = g.to_directed()
    for i, j, d in dg.edges(data=True):
        try:
            t[i,j] = d['t']
        except KeyError:
            t[i,j] = 0
        obj = w[j]
        if i == S:
            obj = w[i] + w[j]
        name = 'x_' + str(i) + '_' + str(j)
        x[i,j] = model.addVar(obj=obj, vtype=grb.GRB.BINARY, name=name)

    model.modelSense = grb.GRB.MAXIMIZE
    model.update()

    RN = range(1, N+1)

    # Path starts at S and ends at T
    model.addConstr(grb.quicksum(x[S,j] for j in RN if (S, j) in x) == 1)
    model.addConstr(grb.quicksum(x[i,T] for i in RN if (i, T) in x) == 1)
    # No edges "entering" S or "leaving" T
    for i in RN:
        if (i, S) in x:
            model.addConstr(x[i,S] == 0)
        if (T, i) in x:
            model.addConstr(x[T,i] == 0)
    # "Flow conservation" constraints
    for k in RN:
        if k != S and k != T:
            model.addConstr(
                grb.quicksum(x[i,k] for i in RN if (i, k) in x) <= 1)
            model.addConstr(
                grb.quicksum(x[k,j] for j in RN if (k, j) in x) <= 1)
            model.addConstr(
                grb.quicksum(x[i,k] for i in RN if i != T and (i, k) in x) +
                grb.quicksum(-x[k,j] for j in RN if j != S and (k, j) in x)
                == 0)
    # Edge budget constraint
    model.addConstr(grb.quicksum(t[i,j]*x[i,j] for (i, j) in x) <= EB)
    # Node budget constraint
    model.addConstr(grb.quicksum(m[j]*x[i,j] for (i, j) in x) <= NB)
    # Subtour elimination constraints (1)
    for k in RN:
        if k != S:
            model.addConstr(u[k] >= 2)
            model.addConstr(u[k] <= N)
    model.addConstr(u[S] == 1)
    # Subtour elimination constraints (2)
    for (i, j) in x:
        if i != S and j != S:
            model.addConstr(u[i] - u[j] + (N-1)*x[i,j] <= N-2)

    model.update()

    # Solve
    model.setParam('TimeLimit', time_limit)
    model.optimize()

    # Decode solution
    if (model.status != grb.GRB.status.OPTIMAL and
        model.status != grb.GRB.status.TIME_LIMIT and
        model.status != grb.GRB.status.INTERRUPTED):
        obj = None
        path = None
    else:
        obj = model.objVal
        nxt = dict()
        for i in RN:
            for j in RN:
                if (i, j) in x and x[i,j].x == 1:
                    nxt[i] = j
        path = [S]
        v = S
        while v != T:
            v = nxt[v]
            path.append(v)
    return (model.status, obj, path)
