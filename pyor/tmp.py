import random
import networkx as nx
import core
import util


g = core.create_graph()
core.plot_graph(g)
core.update_graph(g, radius=200)
ws = nx.get_node_attributes(g, 'w')
sws = sorted(ws.values())[-15:]
cutoff = sws[0]
for v in g.photo_nodes():
    if ws[v] < cutoff:
        g.remove_node(v)
    else:
        g.node[v]['w'] = 1
core.plot_graph(g)
