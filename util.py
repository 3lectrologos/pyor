import json
import csv
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import scipy.spatial as sp
import geopy.distance
import shapely as sply


def read_osm_file(fin):
    with open('roads_large.json') as f:
        data = json.load(f)
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

def read_photo_locations(fin):
    with open(fin, 'r') as tsvin:
        tsvin = csv.reader(tsvin, delimiter=',')
        locs = [(float(row[0]), float(row[1])) for row in tsvin]
    return locs

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

class OsmGraph(nx.Graph):
    def __init__(self, osm_file):
        nx.Graph.__init__(self)
        (nodes, coords, ways) = read_osm_file(osm_file)
        self.ways = ways
        n = len(nodes)
        n2o = dict(n for n in enumerate(nodes, start=1))
        o2n = dict(zip(nodes, range(1, n+1)))
        pos = dict((k, coords[n2o[k]]) for k in range(1, n+1))
        for i in range(1, n+1):
            self.add_node(i, pos=pos[i], w=0, m=0)
        for w in ways:
            for i in range(1, len(w)):
                c1 = coords[w[i-1]]
                c2 = coords[w[i]]
                t = geopy.distance.vincenty(c1, c2).meters
                self.add_edge(o2n[w[i-1]], o2n[w[i]], t=t)
        self.pos = pos

    def photo_nodes(self):
        return [v[0] for v in self.nodes(data=True)
                if v[1].has_key('photo') and v[1]['photo'] == True]

    def plot(self, show_labels=False):
        nodes = nx.draw_networkx_nodes(self,
                                       self.pos,
                                       node_size=NODE_SIZE_NORMAL,
                                       node_color=NODE_COLOR_NORMAL)
        if nodes != None:
            nodes.set_edgecolor(NODE_BORDER_COLOR_NORMAL)
        nodes = nx.draw_networkx_nodes(self,
                                       self.pos,
                                       nodelist=self.photo_nodes(),
                                       node_shape=NODE_SHAPE_PHOTO,
                                       node_size=NODE_SIZE_PHOTO,
                                       node_color=NODE_COLOR_PHOTO)
        if nodes != None:
            nodes.set_edgecolor(NODE_BORDER_COLOR_PHOTO)
        if show_labels:
            nx.draw_networkx_labels(self,
                                    self.pos,
                                    font_color=LABEL_COLOR_NORMAL,
                                    font_size=LABEL_FONT_SIZE_NORMAL)
        nx.draw_networkx_edges(self,
                               self.pos,
                               width=EDGE_WIDTH_NORMAL,
                               edge_color=EDGE_COLOR_NORMAL)

    def plot_path(self, path):
        if path == None:
            edgelist = []
        else:
            edgelist = zip(path[:-1], path[1:])
        if edgelist == []:
            return
        nodes = nx.draw_networkx_nodes(self,
                                       self.pos,
                                       nodelist=path,
                                       node_size=NODE_SIZE_PATH,
                                       node_color=NODE_COLOR_PATH)
        if nodes != None:
            nodes.set_edgecolor(NODE_BORDER_COLOR_PATH)
        photo_path_nodes = list(set(path) & set(self.photo_nodes()))
        if photo_path_nodes != []:
            nodes = nx.draw_networkx_nodes(self,
                                           self.pos,
                                           nodelist=photo_path_nodes,
                                           node_shape=NODE_SHAPE_PHOTO,
                                           node_size=NODE_SIZE_PATH,
                                           node_color=NODE_COLOR_PHOTO_PATH)
        if nodes != None:
            nodes.set_edgecolor(NODE_BORDER_COLOR_PATH)
        nx.draw_networkx_edges(self,
                               self.pos,
                               edgelist=edgelist,
                               width=EDGE_WIDTH_PATH,
                               edge_color=EDGE_COLOR_PATH)

    def add_photo_nodes(self, photo_locs):
        photo_locs = np.array(photo_locs)
        n = self.number_of_nodes()
        kd = sp.KDTree(np.array(self.pos.values()))
        idxs = list(kd.query(photo_locs)[1])
        k = 1
        for i, idx in enumerate(idxs):
            nni = self.pos.keys()[idx]
            nnc = self.pos.values()[idx]
            # Photo node
            self.add_node(n+k, w=1, m=1, photo=True)
            self.pos[n+k] = (photo_locs[i,0], photo_locs[i,1])
            self.add_edge(nni, n+k, t=0)
            k = k + 1
            # Aux node on top of nearest node
            self.add_node(n+k, w=0, m=0)
            self.pos[n+k] = (nnc[0], nnc[1])
            es = self.edge[nni]
            for v in es:
                self.add_edge(n+k, v, t=es[v]['t'])
            k = k + 1

def show():
    plt.subplots_adjust(left=0.001, right=0.999, top=0.999, bottom=0.001)
    plt.show()

def node_cover_area(ps, radius=0.001):
    u = sply.ops.cascaded_union(sply.geometry.Point(p).buffer(radius) for p in ps)
    return u.area

def plot_cover(ps, radius=0.001):
    pass
