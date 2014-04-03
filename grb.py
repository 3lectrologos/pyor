"""
Formulate and solve orienteering problem for a given NetworkX graph.
"""
import time
import networkx as nx
import pylab as plt
import gurobipy as grb
import util

DEBUG = True

NODE_COLOR_NORMAL = '#5555EE'
NODE_COLOR_PHOTO = '#E6D030'
NODE_COLOR_PHOTO_PATH = '#EE3333'
NODE_BORDER_COLOR_NORMAL = '0.2'
NODE_BORDER_COLOR_PHOTO = '0.2'
NODE_COLOR_PATH = '#009926'
NODE_BORDER_COLOR_PATH = '0.2'
NODE_SIZE_NORMAL = 40
NODE_SIZE_PHOTO = 60
NODE_SIZE_PATH = 80
NODE_SIZE_PHOTO_PATH = 100
NODE_SHAPE_PHOTO = 's'
LABEL_COLOR_NORMAL = '0.1'
LABEL_FONT_SIZE_NORMAL = 11
EDGE_COLOR_NORMAL = '0.2'
EDGE_WIDTH_NORMAL = 1.5
EDGE_COLOR_PATH = '#009926'
EDGE_WIDTH_PATH = 3.0

def find_path(g, start, end, budget, minnodes, maxnodes, dry=False):
    if start != end:
        return find_path_aux(g, start, end, budget, minnodes, maxnodes, dry)
    else:
        startedges = g.edges(start, data=True)
        dummy = g.number_of_nodes() + 1
        g.add_node(dummy, w=0)
        for (u, v, d) in startedges:
            assert u == start
            g.add_edge(v, dummy, t=d['t'])
        (solstatus, obj, path) = find_path_aux(g, start, dummy,
                                               budget, minnodes, maxnodes, dry)
        g.remove_node(dummy)
        if path != None:
            assert path[-1] == dummy
            path[-1] = start
        return (solstatus, obj, path)

def find_path_aux(g, start, end, budget, minnodes, maxnodes, dry=False):
    # Problem parameters
    N = g.number_of_nodes()
    S = start
    T = end
    B = budget
    ML = minnodes
    MH = maxnodes

    if DEBUG:
        print '(N, S, T, B, ML, MH) =', ','.join(map(str, [N, S, T, B, ML, MH]))
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
            model.addConstr(grb.quicksum(x[i,k] for i in RN if (i, k) in x) <= 1)
            model.addConstr(grb.quicksum(x[k,j] for j in RN if (k, j) in x) <= 1)
            model.addConstr(grb.quicksum(x[i,k] for i in RN if i != T and (i, k) in x) +
                            grb.quicksum(-x[k,j] for j in RN if j != S and (k, j) in x) == 0)
    # Edge budget constraint
    #model.setObjective(grb.quicksum(t[i,j]*x[i,j] for (i, j) in x), grb.GRB.MINIMIZE)
    model.addConstr(grb.quicksum(t[i,j]*x[i,j] for (i, j) in x) <= B)
    # Vertex budget constraints
    #model.addConstr(grb.quicksum(m[j]*x[i,j] for (i, j) in x) >= ML)
    model.addConstr(grb.quicksum(m[j]*x[i,j] for (i, j) in x) <= MH)
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

    # Write problem to lp file
    #model.write('mip.lp')

    if dry == True:
        return (None, None, None)
    
    # Solve
    model.optimize()

    # If optimal plot path in graph
    if model.status != grb.GRB.status.OPTIMAL and model.status != grb.GRB.status.INTERRUPTED:
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

def show_custom():
    plt.subplots_adjust(left=0.001, right=0.999, top=0.999, bottom=0.001)
    plt.show()

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
    nodes = nx.draw_networkx_nodes(g,
                                   pos,
                                   nodelist=util.get_photo_nodes(g),
                                   node_shape=NODE_SHAPE_PHOTO,
                                   node_size=NODE_SIZE_PHOTO,
                                   node_color=NODE_COLOR_PHOTO)
    nodes.set_edgecolor(NODE_BORDER_COLOR_PHOTO)
#    nx.draw_networkx_labels(g,
#                            pos,
#                            font_color=LABEL_COLOR_NORMAL,
#                            font_size=LABEL_FONT_SIZE_NORMAL)
    nx.draw_networkx_edges(g,
                           pos,
                           width=EDGE_WIDTH_NORMAL,
                           edge_color=EDGE_COLOR_NORMAL)
    print 'path =', path
    if path == None or path == []:
        show_custom()
        return
    nodes = nx.draw_networkx_nodes(g,
                                   pos,
                                   nodelist=path,
                                   node_size=NODE_SIZE_PATH,
                                   node_color=NODE_COLOR_PATH)
    nodes.set_edgecolor(NODE_BORDER_COLOR_PATH)
    photo_path_nodes = list(set(path) & set(util.get_photo_nodes(g)))
    if photo_path_nodes != []:
        nodes = nx.draw_networkx_nodes(g,
                                       pos,
                                       nodelist=photo_path_nodes,
                                       node_shape=NODE_SHAPE_PHOTO,
                                       node_size=NODE_SIZE_PATH,
                                       node_color=NODE_COLOR_PHOTO_PATH)
        nodes.set_edgecolor(NODE_BORDER_COLOR_PATH)
    nx.draw_networkx_edges(g,
                           pos,
                           edgelist=edgelist,
                           width=EDGE_WIDTH_PATH,
                           edge_color=EDGE_COLOR_PATH)
    show_custom()

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
    g = demo_graph_small()
    (status, objective, path) = find_path(g, start=1, end=1,
                                          budget=30, maxnodes=10)
    print 'Status: ', status
    print 'Objective = ', objective
    plot_path(g, path)
