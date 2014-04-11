import os.path
import pickle
import math
import networkx as nx
import matplotlib.pyplot as plt
import mip
import util


FILE_GRAPH = 'graph.pickle'
RADIUS = 100

def create_graph(radius):
    pn = g.photo_nodes()
    d = {foo: g.pos[foo] for foo in pn}
    perm, gains = util.greedy_cover({foo: g.pos[foo] for foo in pn}, radius)
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

photo_locs = util.read_photo_locations('photo_coords.csv')
g = util.OsmGraph('roads_large.json')
g.add_photo_nodes(photo_locs)

s = 1315
t = 2000

if os.path.isfile(FILE_GRAPH):
    g = load_graph(FILE_GRAPH)
else:
    g = create_graph(RADIUS)
    save_graph(g, FILE_GRAPH)

plot(cover=True)

(status, objective, path) = mip.find_path(g,
                                          start=s,
                                          end=t,
                                          edge_budget=3000,
                                          node_budget=10)

print 'Covered area =', util.cover_area([g.pos[u] for u in path], RADIUS)
plot(path=path)
