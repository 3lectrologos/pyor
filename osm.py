import json
import csv
import numpy as np
import scipy.spatial as sp
import matplotlib.pyplot as plt
import networkx as nx
import geopy.distance
import grb
import util


DEBUG = False

NODE_COLOR_NORMAL = '#5555EE'
NODE_BORDER_COLOR_NORMAL = '0.2'
NODE_SIZE_NORMAL = 60
EDGE_COLOR_NORMAL = '0.2'
EDGE_WIDTH_NORMAL = 1.5

def filter_data(data):
    coords = {}
    ways = []
    for d in data['elements']:
        if d['type'] == 'node':
            coords[int(d['id'])] = (d['lon'], d['lat'])
        if d['type'] != 'way':
            continue
        tags = d['tags']
        if 'area' in tags and tags['area'] == 'yes':
            continue
        if 'access' in tags and tags['access'] == 'private':
            continue
        ways.append(d['nodes'])
    nodes = set([a for b in ways for a in b])
    coords = dict((k, v) for k, v in coords.iteritems() if k in nodes)
    return (nodes, coords, ways)

with open('roads_large.json') as f:
    data = json.load(f)

(nodes, coords, ways) = filter_data(data)

n = len(nodes)
n2o = dict(n for n in enumerate(nodes, start=1))
o2n = dict(zip(nodes, range(1, n+1)))
cn = dict((k, coords[n2o[k]]) for k in range(1, n+1))
g = nx.Graph()
for i in range(1, n+1):
    g.add_node(i, pos=cn[i], w=0, m=0)

for w in ways:
    for i in range(1, len(w)):
        c1 = coords[w[i-1]]
        c2 = coords[w[i]]
        t = geopy.distance.vincenty(c1, c2).meters
        g.add_edge(o2n[w[i-1]], o2n[w[i]], t=t)

# Read photo locations
with open('photo_coords.csv', 'r') as tsvin:
    tsvin = csv.reader(tsvin, delimiter=',')
    locs = np.array([(float(row[0]), float(row[1])) for row in tsvin])
# Plot photo locations
#plt.plot(locs[:,0], locs[:,1], 'ro')
# Find nearest node of each photo location
kd = sp.KDTree(np.array(cn.values()))
idxs = list(kd.query(locs)[1])
k = 1
for i, idx in enumerate(idxs):
    nni = cn.keys()[idx]
    nnc = cn.values()[idx]
    #plt.plot(nnc[0], nnc[1], 'yo')
    # Photo node
    g.add_node(n+k, w=1, m=1, photo=True)
    cn[n+k] = (locs[i,0], locs[i,1])
    g.add_edge(nni, n+k, t=0)
    k = k + 1
    # Aux node on top of nearest node
    g.add_node(n+k, w=0, m=0)
    cn[n+k] = (nnc[0], nnc[1])
#    g.edge[n+k] = g.edge[nni]
    es = g.edge[nni]
    for v in es:
        g.add_edge(n+k, v, t=es[v]['t'])
    k = k + 1

(status, objective, path) = grb.find_path(g, start=2515, end=42, budget=3500,
                                          minnodes=5, maxnodes=10)
print (status, objective, path)
grb.plot_path(g, path, pos=cn)

if DEBUG:
    nodes_dr = nx.draw_networkx_nodes(g,
                                      cn,
                                      node_size=NODE_SIZE_NORMAL,
                                      node_color=NODE_COLOR_NORMAL)
    nodes_dr.set_edgecolor(NODE_BORDER_COLOR_NORMAL)
    nx.draw_networkx_edges(g,
                           cn,
                           width=EDGE_WIDTH_NORMAL,
                           edge_color=EDGE_COLOR_NORMAL)
    plt.show()
