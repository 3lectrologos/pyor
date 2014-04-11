import json
import csv
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.markers
import matplotlib.collections
import matplotlib.patches
import scipy.spatial as sp
import geopy.distance
import shapely.geometry
import shapely.ops
import mpl_toolkits.basemap as bsmp


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
NODE_COLOR_PHOTO_PATH = '#E52917'
NODE_BORDER_COLOR_NORMAL = '0.2'
NODE_BORDER_COLOR_PHOTO = '0.2'
NODE_COLOR_PATH = '#6A990F'
NODE_BORDER_COLOR_PATH = '0.2'
NODE_SIZE_NORMAL = 15
NODE_ALPHA_NORMAL = 0.7
NODE_SIZE_PHOTO_MIN = 20
NODE_SIZE_PHOTO_SCALE = 100
NODE_SIZE_PATH = 30
NODE_SHAPE_PHOTO = 's'
LABEL_COLOR_NORMAL = '0.1'
LABEL_FONT_SIZE_NORMAL = 11
EDGE_COLOR_NORMAL = '0.2'
EDGE_ALPHA_NORMAL = 0.3
EDGE_WIDTH_NORMAL = 1.5
EDGE_COLOR_PATH = '#6A990F'
EDGE_WIDTH_PATH = 3.0
NODE_LINEWIDTH_NORMAL = 0.5

NODE_SIZE_ST = 200
NODE_COLOR_ST = '#47660A'
NODE_BORDER_COLOR_ST = '0.2'
NODE_LINEWIDTH_ST = 0.5
NODE_SIZE_ST_INNER = 60
NODE_COLOR_ST_INNER = '#6A990F'
NODE_BORDER_COLOR_ST_INNER = '0.2'
NODE_LINEWIDTH_ST_INNER = 0.5

COVER_ALPHA = 0.1

class OsmGraph(nx.Graph):
    def __init__(self, osm_file):
        nx.Graph.__init__(self)
        (nodes, coords, ways) = read_osm_file(osm_file)
        cproj = coords.values()[0]
        self.mp = bsmp.Basemap(projection='ortho',
                               lon_0=cproj[0],
                               lat_0=cproj[1])
        for k, v in coords.iteritems():
            coords[k] = self.mp(v[0], v[1])
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
                t = np.linalg.norm((c1[0]-c2[0], c1[1]-c2[1]))
                self.add_edge(o2n[w[i-1]], o2n[w[i]], t=t)
        self.pos = pos

    def photo_nodes(self):
        return [v[0] for v in self.nodes(data=True)
                if v[1].has_key('photo') and v[1]['photo'] == True]

    def plot(self, show_labels=False):
        nodes = nx.draw_networkx_nodes(self,
                                       self.pos,
                                       node_size=NODE_SIZE_NORMAL,
                                       node_color=NODE_COLOR_NORMAL,
                                       linewidths=NODE_LINEWIDTH_NORMAL,
                                       alpha=NODE_ALPHA_NORMAL)
        if nodes != None:
            nodes.set_edgecolor(NODE_BORDER_COLOR_NORMAL)
        ws = nx.get_node_attributes(self, 'w')
        sizes = [NODE_SIZE_PHOTO_MIN + ws[v]*NODE_SIZE_PHOTO_SCALE
                 for v in self.photo_nodes()]
        nodes = nx.draw_networkx_nodes(self,
                                       self.pos,
                                       nodelist=self.photo_nodes(),
                                       node_shape=NODE_SHAPE_PHOTO,
                                       node_size=sizes,
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
                               edge_color=EDGE_COLOR_NORMAL,
                               alpha=EDGE_ALPHA_NORMAL)

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
        ws = nx.get_node_attributes(self, 'w')
        photo_path_nodes = list(set(path) & set(self.photo_nodes()))
        if photo_path_nodes != []:
            sizes = [NODE_SIZE_PHOTO_MIN + ws[v]*NODE_SIZE_PHOTO_SCALE
                     for v in photo_path_nodes]
            nodes = nx.draw_networkx_nodes(self,
                                           self.pos,
                                           nodelist=photo_path_nodes,
                                           node_shape=NODE_SHAPE_PHOTO,
                                           node_size=sizes,
                                           node_color=NODE_COLOR_PHOTO_PATH)
        if nodes != None:
            nodes.set_edgecolor(NODE_BORDER_COLOR_PATH)
        nx.draw_networkx_edges(self,
                               self.pos,
                               edgelist=edgelist,
                               width=EDGE_WIDTH_PATH,
                               edge_color=EDGE_COLOR_PATH)

    def plot_st(self, s, t):
        nodes = nx.draw_networkx_nodes(self,
                                       self.pos,
                                       nodelist=[s, t],
                                       node_size=NODE_SIZE_ST,
                                       node_color=NODE_COLOR_ST,
                                       linewidths=NODE_LINEWIDTH_ST)
        if nodes != None:
            nodes.set_edgecolor(NODE_BORDER_COLOR_ST)
        nodes = nx.draw_networkx_nodes(self,
                                       self.pos,
                                       nodelist=[s, t],
                                       node_size=NODE_SIZE_ST_INNER,
                                       node_color=NODE_COLOR_ST_INNER,
                                       linewidths=NODE_LINEWIDTH_ST_INNER)
        if nodes != None:
            nodes.set_edgecolor(NODE_BORDER_COLOR_ST_INNER)

    def add_photo_nodes(self, photo_locs):
        photo_locs = [self.mp(i, j) for i, j in photo_locs]
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
    plt.axis('equal')
    plt.gca().set_xlim((6370000, 6372000))
    plt.gca().set_ylim((6370000, 6372000))
    plt.show()

def draw():
    plt.subplots_adjust(left=0.001, right=0.999, top=0.999, bottom=0.001)
    plt.axis('equal')
    plt.draw()

def cover_area(ps, radius):
    u = shapely.ops.cascaded_union(
        [shapely.geometry.Point(p).buffer(radius) for p in ps])
    return u.area

def plot_cover(ps, radius):
    ax = plt.gca()
    col = matplotlib.collections.PatchCollection(
        [matplotlib.patches.Circle(p, radius) for p in ps],
        alpha=COVER_ALPHA)
    ax.add_collection(col)

def greedy_cover(ps, radius):
    ps = {k: shapely.geometry.Point(v).buffer(radius)
          for k, v in ps.iteritems()}
    k, u = ps.popitem()
    perm = [k]
    totalarea = u.area
    gains = [totalarea]
    while ps != {}:
        print len(ps)
        mgain = {k: u.union(v).area for k, v in ps.iteritems()}
        maxi, maxval = max(mgain.iteritems(), key=lambda x: x[1])
        perm.append(maxi)
        gains.append(maxval - totalarea)
        totalarea = maxval
        u = u.union(ps[maxi])
        del ps[maxi]
    return (perm, gains)

def subg(f, v, y):
    assert set(y) <= set(v)
    perm = list(y) + list(set(v) - set(y))
    h = {}
    vals = [0]
    for i in range(1, len(perm)+1):
        val = f(perm[:i]) - sum(vals)
        h[perm[i-1]] = val
        vals.append(val)
    c = f(y) - sum(vals[:len(y)+1])
    return lambda x: c + sum(h[e] for e in x)
