import os.path
import pickle
import math
import networkx as nx
import matplotlib.pyplot as plt
import mip
import util


FILE_GRAPH = 'graph.pickle'
RADIUS = 100

def create_graph():
    photo_locs = util.read_photo_locations('photo_coords.csv')
    g = util.OsmGraph('roads_large.json')
    g.add_photo_nodes(photo_locs)
    return g

def update_graph(g, radius, prev=None):
    pn = g.photo_nodes()
    if prev == None:
        perm, gains, _ = util.greedy_cover({u: g.pos[u] for u in pn},
                                           radius=radius)
    else:
        xn = g.photo_nodes(prev)
        perm1, gains1, cov = util.greedy_cover({u: g.pos[u] for u in xn},
                                             radius=radius)
        rest = list(set(pn) - set(xn))
        print '----'
        perm2, gains2, _ = util.greedy_cover({u: g.pos[u] for u in rest},
                                            radius=radius,
                                            ug=cov)
        perm = perm1 + perm2
        gains = gains1 + gains2
    weights = dict(zip(perm, [gain/(math.pi*radius**2) for gain in gains]))
    nx.set_node_attributes(g, 'w', weights)
    return g

def save_graph(g, path):
    with open(path, 'w') as fout:
        pickle.dump(g, fout)

def load_graph(path):
    with open(path, 'r') as fin:
        return pickle.load(fin)

def plot(path=[], cover=False):
    plt.clf()
    g.plot()
    g.plot_path(path)
    g.plot_st(s, t)
    if cover:
        util.plot_cover([g.pos[u] for u in g.photo_nodes()], RADIUS)
    # util.draw()
    # plt.gcf().set_size_inches(32, 18)
    # plt.savefig('init.pdf', format='pdf', bbox_inches='tight')
    util.show()    

s = 1315
t = 2000

#if os.path.isfile(FILE_GRAPH):
#    g = load_graph(FILE_GRAPH)
#else:
#    g = create_graph()
#    update_graph(g, RADIUS)
#    save_graph(g, FILE_GRAPH)

g = create_graph()
update_graph(g, RADIUS)
plot(cover=True)

(status, objective, path) = mip.find_path(g,
                                          start=s,
                                          end=t,
                                          edge_budget=3000,
                                          node_budget=10)

print 'Covered area =', util.cover_area([g.pos[u] for u in path], RADIUS)
plot(path=path)

update_graph(g, RADIUS, prev=path)
plot(path=path)
(status, objective, path) = mip.find_path(g,
                                          start=s,
                                          end=t,
                                          edge_budget=3000,
                                          node_budget=10)
plot(path=path)
