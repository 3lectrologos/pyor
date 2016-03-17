import math
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
    with open(fin) as f:
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
        ids, locs = [], []
        i = 0
        for row in tsvin:
            # Note: Order is (longitude, latitude)
            locs.append((float(row[1]), float(row[0])))
            ids.append(i)
            i += 1
    return (ids, locs)

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
LABEL_FONT_SIZE_NORMAL = 6
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
        self.kd = sp.KDTree(np.array(self.pos.values()))

    def photo_nodes(self, vs=None):
        photonodes = [v[0] for v in self.nodes(data=True)
                      if v[1].has_key('photo') and v[1]['photo'] == True]
        if vs == None:
            return photonodes
        else:
            return list(set(photonodes) & set(vs))

    def is_photo_node(self, v):
        return self.node[v].has_key('photo') and self.node[v]['photo'] == True

    def plot(self, show_labels=False, photo_nodes=True):
        # nodes = nx.draw_networkx_nodes(self,
        #                                self.pos,
        #                                node_size=NODE_SIZE_NORMAL,
        #                                node_color=NODE_COLOR_NORMAL,
        #                                linewidths=NODE_LINEWIDTH_NORMAL,
        #                                alpha=NODE_ALPHA_NORMAL)
        # if nodes != None:
        #     nodes.set_edgecolor(NODE_BORDER_COLOR_NORMAL)
        if photo_nodes:
            ws = nx.get_node_attributes(self, 'w')
            nodes = nx.draw_networkx_nodes(self,
                                           self.pos,
                                           nodelist=self.photo_nodes(),
                                           node_shape=NODE_SHAPE_PHOTO,
                                           node_size=80,
                                           node_color=NODE_COLOR_PHOTO)
            sel1 = [self.photo_nodes()[i] for i in [10, 25, 39]]
            nodes = nx.draw_networkx_nodes(self,
                                           self.pos,
                                           nodelist=sel1,
                                           node_shape=NODE_SHAPE_PHOTO,
                                           node_size=80,
                                           node_color=NODE_COLOR_PHOTO_PATH)
            sel2 = [self.photo_nodes()[i] for i in [2, 5, 16, 18, 27, 41]]
            nodes = nx.draw_networkx_nodes(self,
                                           self.pos,
                                           nodelist=sel2,
                                           node_shape=NODE_SHAPE_PHOTO,
                                           node_size=80,
                                           node_color=NODE_COLOR_ST)
            sel3 = [self.photo_nodes()[i] for i in [15, 17, 34]]
            nodes = nx.draw_networkx_nodes(self,
                                           self.pos,
                                           nodelist=sel3,
                                           node_shape=NODE_SHAPE_PHOTO,
                                           node_size=80,
                                           node_color=NODE_COLOR_NORMAL)
            if nodes != None:
                nodes.set_edgecolor(NODE_BORDER_COLOR_PHOTO)
        if show_labels:
            nx.draw_networkx_labels(self,
                                    self.pos,
                                    labels=dict(zip(self.photo_nodes(), [str(i) for i in range(len(self.photo_nodes()))])),
                                    font_color=LABEL_COLOR_NORMAL,
                                    font_size=LABEL_FONT_SIZE_NORMAL)
        # nx.draw_networkx_edges(self,
        #                        self.pos,
        #                        width=EDGE_WIDTH_NORMAL,
        #                        edge_color=EDGE_COLOR_NORMAL,
        #                        alpha=EDGE_ALPHA_NORMAL)

    def plot_path(self, path, weights=True):
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
        photo_path_nodes = self.photo_nodes(path)
        if photo_path_nodes != []:
            if weights:
                sizes = [NODE_SIZE_PHOTO_MIN + ws[v]*NODE_SIZE_PHOTO_SCALE
                         for v in photo_path_nodes]
            else:
                sizes = [NODE_SIZE_PHOTO_MIN + NODE_SIZE_PHOTO_SCALE
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

    def add_photo_nodes(self, ids, locs):
        locs = np.array([self.mp(i, j) for i, j in locs])
        n = self.number_of_nodes()
        idxs = list(self.kd.query(locs)[1])
        k = 1
        for i, idx in enumerate(idxs):
            nni = self.pos.keys()[idx]
            nnc = self.pos.values()[idx]
            # Photo node
            self.add_node(n+k, w=1, m=1, photo=True, id=ids[i])
            self.pos[n+k] = (locs[i,0], locs[i,1])
            self.add_edge(nni, n+k, t=0)
            k = k + 1
            # Aux node on top of nearest node
            self.add_node(n+k, w=0, m=0)
            self.pos[n+k] = (nnc[0], nnc[1])
            es = self.edge[nni]
            for v in es:
                self.add_edge(n+k, v, t=es[v]['t'])
            k = k + 1
        self.kdp = sp.KDTree(np.array(self.pos.values()))


    def nodes_in_radius(self, nodes, radius):
        x = np.array([self.pos[node] for node in nodes])
        keys = self.pos.keys()
        return [keys[i] for sl in self.kdp.query_ball_point(x, radius) for i in sl]

    def nearest_node(self, coords):
        return self.pos.keys()[self.kd.query(
                np.array(self.mp(coords[0], coords[1])))[1]]

def show():
    plt.subplots_adjust(left=0.001, right=0.999, top=0.999, bottom=0.001)
    plt.axis('equal')
    #plt.gca().set_xlim((6370000, 6372000))
    #plt.gca().set_ylim((6370000, 6372000))
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

def greedy_cover(ps, radius, ug=None, verbose=True):
    ps = {k: shapely.geometry.Point(v).buffer(radius)
          for k, v in ps.iteritems()}
    k, u = ps.popitem()
    perm = [k]
    if ug == None:
        totalarea = u.area
        gains = [totalarea]
    else:
        u = ug.union(u)
        totalarea = u.area
        gains = [totalarea - ug.area]
    while ps != {}:
        if verbose:
            print len(ps)
        mgain = {k: u.union(v).area for k, v in ps.iteritems()}
        _, maxval = max(mgain.iteritems(), key=lambda x: x[1])
        allmax = [k for k, v in mgain.iteritems() if v == maxval]
        maxi = np.random.choice(allmax)
        perm.append(maxi)
        gains.append(maxval - totalarea)
        totalarea = maxval
        u = u.union(ps[maxi])
        del ps[maxi]
    # TODO: Could add a treshold here---if it covers less than eps, set its
    #       gain to zero---to avoid having these small-contribution waypoints
    #       that don't look good in the final solutions.
    gains = [g/(math.pi*radius*radius) for g in gains]
    return (perm, gains, u)

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
