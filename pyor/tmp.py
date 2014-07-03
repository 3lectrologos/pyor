import networkx as nx
import core
import util
import mip


S = 250
T = 20
RADIUS = 150
LENGTH_RATIO = 2

g = core.create_graph()
path = nx.shortest_path(g, S, T, weight='t')
splen = 0
for i in range(len(path)-1):
    splen = splen + g.edge[path[i]][path[i+1]]['t']
print 'splen =', splen
nr = g.nodes_in_radius(path, RADIUS)
core.plot_graph(g, S, T, nr)
g.remove_nodes_from(set(g.nodes()) - set(nr))
nc = nx.node_connected_component(g, S)
g.remove_nodes_from(set(g.nodes()) - set(nc))
core.update_graph(g, core.RADIUS)
core.plot_graph(g, S, T)
(status, objective, path) = mip.find_path(g,
                                          start=S,
                                          end=T,
                                          edge_budget=LENGTH_RATIO*splen,
                                          node_budget=10,
                                          time_limit=20,
                                          verbose=True)
print path
core.plot_graph(g, S, T, path=path, cover=False)
