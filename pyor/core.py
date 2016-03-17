import os.path
import pickle
import math
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import scipy.spatial as sp
import util


DATA_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data')
FILE_GRAPH = os.path.join(DATA_DIR, 'graph.pickle')
PHOTOS_FILE = os.path.join(DATA_DIR, 'path_set_50_items.csv')
ROADS_FILE = os.path.join(DATA_DIR, 'roads_large.json')
MIN_WEIGHT = 0
RADIUS = 70

def create_graph():
    (ids, locs) = util.read_photo_locations(PHOTOS_FILE)
    print ids, locs
    g = util.OsmGraph(ROADS_FILE)
    g.add_photo_nodes(ids, locs)
    return g

def update_graph(g, radius, prev=None, verbose=True):
    pn = g.photo_nodes()
    if prev == None:
        perm, gains, _ = util.greedy_cover({u: g.pos[u] for u in pn},
                                           radius=radius, verbose=verbose)
    else:
        xn = g.photo_nodes(prev)
        perm1, gains1, cov = util.greedy_cover({u: g.pos[u] for u in xn},
                                               radius=radius, verbose=verbose)
        rest = list(set(pn) - set(xn))
        if verbose:
            print '----'
        perm2, gains2, _ = util.greedy_cover({u: g.pos[u] for u in rest},
                                             radius=radius,
                                             ug=cov,
                                             verbose=verbose)
        perm = perm1 + perm2
        gains = gains1 + gains2
    weights = dict(zip(perm, [max(MIN_WEIGHT, gain) for gain in gains]))
    nx.set_node_attributes(g, 'w', weights)
    return g

def save_graph(g, path):
    with open(path, 'w') as fout:
        pickle.dump(g, fout)

def load_graph(path):
    with open(path, 'r') as fin:
        return pickle.load(fin)

def plot_graph(g, s=None, t=None, path=[], cover=False, radius=0, weights=True, photo_nodes=True):
    plt.clf()
    g.plot(photo_nodes=photo_nodes, show_labels=True)
    g.plot_path(path, weights=weights)
    if s is not None and t is not None:
        g.plot_st(s, t)
    if cover:
        util.plot_cover([g.pos[u] for u in g.photo_nodes()], radius)
    util.show()    

def get_path(s, t, node_budget=10, edge_budget=2000, time_limit=10,
             plot=False, verbose=False, coords=True):
    g = create_graph()
    if coords:
        s = g.nearest_node(s)
        t = g.nearest_node(t)
#        s = g.pos.keys()[g.kd.query(np.array(g.mp(s[0], s[1])))[1]]
#        t = g.pos.keys()[g.kd.query(np.array(g.mp(t[0], t[1])))[1]]
    update_graph(g, RADIUS, verbose=verbose)
    if plot:
        plot_graph(g, s, t, cover=True, radius=RADIUS)
    path = nx.shortest_path(g, s, t)
    print g.pos
    if plot:
        plot_graph(g, s, t, path=path, cover=False, radius=RADIUS)
    return [g.node[w]['id'] for w in path if g.is_photo_node(w)]
