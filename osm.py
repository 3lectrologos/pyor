import json
import networkx as nx
import matplotlib.pyplot as plt
import mip


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

with open('roads_small.json') as f:
    data = json.load(f)

(nodes, coords, ways) = filter_data(data)

n = len(nodes)
n2o = dict(n for n in enumerate(nodes, start=1))
o2n = dict(zip(nodes, range(1, n+1)))
cn = dict((k, coords[n2o[k]]) for k in range(1, n+1))
g = nx.Graph()
for i in range(1, n+1):
    g.add_node(i, pos=cn[i], w=1)

for w in ways:
    for i in range(1, len(w)):
        g.add_edge(o2n[w[i-1]], o2n[w[i]], t=1)
        c1 = coords[w[i-1]]
        c2 = coords[w[i]]
        x = [c1[0], c2[0]]
        y = [c1[1], c2[1]]

(status, objective, path) = mip.find_path(g, start=110, end=90,
                                          budget=50, maxnodes=15)
print (status, objective, path)
mip.plot_path(g, path, pos=cn)

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
