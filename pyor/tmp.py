import random
import networkx as nx
import core
import util
import mip

#START = (8.549948, 47.421401)
#START = (8.538508, 47.375589)
#END = (8.543569, 47.369951)
#START = (random.uniform(8.53, 8.55), random.uniform(47.36, 47.38))
#END = (random.uniform(8.53, 8.55), random.uniform(47.36, 47.38))
START, END = (8.534931854686034, 47.3763725134755), (8.548649460037252, 47.36761402818917)
print 'START, END =', START, END
LENGTH_RATIO = 1.5


def path_length(g, path):
    plen = 0
    for i in range(len(path)-1):
        plen = plen + g.edge[path[i]][path[i+1]]['t']
    return plen

def subgraph(g, s, t):
    path = nx.shortest_path(g, s, t, weight='t')
    core.plot_graph(g, cover=False, photo_nodes=False)
    core.plot_graph(g, s, t, cover=False, photo_nodes=False)
    core.plot_graph(g, s, t, cover=False)
    splen = path_length(g, path)
    print 'splen =', splen
    radius = 200#max(70, splen/20.0)
    nr = g.nodes_in_radius(path, radius)
    core.plot_graph(g, s, t, nr)
    g.remove_nodes_from(set(g.nodes()) - set(nr))
    nc = nx.node_connected_component(g, s)
    g.remove_nodes_from(set(g.nodes()) - set(nc))
    return splen

g = core.create_graph()
s = g.nearest_node(START)
t = g.nearest_node(END)
splen = subgraph(g, s, t)
core.update_graph(g, core.RADIUS)
core.plot_graph(g, s, t)
(status, objective, path) = mip.find_path(g,
                                          start=s,
                                          end=t,
                                          edge_budget=LENGTH_RATIO*splen,
                                          node_budget=10,
                                          time_limit=30,
                                          verbose=True)
print 'mip pathlen =', path_length(g, path)
core.plot_graph(g, s, t, path=path, cover=False)
selected = [w for w in path if g.is_photo_node(w)]
print selected
perm, gains, _ = util.greedy_cover({u: g.pos[u] for u in selected}, 120)
print perm
print gains
removed = [perm[i] for i in range(len(perm)) if gains[i] < 0.4]
g.pos
path = [p for p in path if p not in removed]
core.plot_graph(g, s, t, path=path, cover=False, weights=False, photo_nodes=False)
