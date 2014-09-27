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
COVER_SIZE = 2
COVER_ANGLE = 45

SKIP_LINES = 6
NUM_NEAREST_NBG = 10

class RoboGraph(nx.DiGraph):
    def __init__(self, fin):
        nx.DiGraph.__init__(self)
        self.pos = {}
        with open(fin, 'r') as tsvin:
            tsvin = csv.reader(tsvin, delimiter='\t')
            for skip in range(SKIP_LINES):
                tsvin.next()
            for row in tsvin:
                node_id = int(row[0])
                x, y, z = int(row[1]), int(row[2]), int(row[3])
                yaw = (int(row[4]), int(row[5]))
                w = float(row[6])
                self.add_node(node_id, pos=(x, y), yaw=yaw, w=w)
                self.pos[node_id] = (x, y)
                BASE = 7
                OFFSET = 3
                for k in range(NUM_NEAREST_NBG):
                    nbg_id = int(row[BASE + k*OFFSET])
                    tout = float(row[BASE + k*OFFSET + 1])
                    tin = float(row[BASE + k*OFFSET + 2])
                    self.add_edge(node_id, nbg_id, t=tout)
                    self.add_edge(nbg_id, node_id, t=tin)
        self.kd = sp.KDTree(np.array(self.pos.values()))

    def plot(self, show_labels=False):
        nodes = nx.draw_networkx_nodes(self,
                                       self.pos,
                                       node_size=NODE_SIZE_NORMAL,
                                       node_color=NODE_COLOR_NORMAL,
                                       linewidths=NODE_LINEWIDTH_NORMAL,
                                       alpha=NODE_ALPHA_NORMAL)
        if nodes != None:
            nodes.set_edgecolor(NODE_BORDER_COLOR_NORMAL)
        if show_labels:
            nx.draw_networkx_labels(self,
                                    self.pos,
                                    font_color=LABEL_COLOR_NORMAL,
                                    font_size=LABEL_FONT_SIZE_NORMAL)
        nx.draw_networkx_edges(self,
                               self.pos,
                               width=EDGE_WIDTH_NORMAL,
                               edge_color=EDGE_COLOR_NORMAL,
                               arrows=False,
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
        nx.draw_networkx_edges(self,
                               self.pos,
                               edgelist=edgelist,
                               arrows=False,
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

    def plot_cover(self):
        ax = plt.gca()
        polys = []
        for v in self.nodes_iter():
            p0 = self.node[v]['pos']
            yaw = self.node[v]['yaw']
            w = COVER_SIZE*(1 - np.exp(-self.node[v]['w']))
            abase = np.radians(COVER_ANGLE)
            a0 = np.angle(yaw[0] + yaw[1]*1j)
            a1 = a0 + abase/2.0
            a2 = a0 - abase/2.0
            p1 = add(p0, rot(a1, x=(w, 0)))
            p2 = add(p0, rot(a2, x=(w, 0)))
            poly = matplotlib.patches.Polygon(np.array([p0, p1, p2]),
                                              closed=True)
            polys.append(poly)
        col = matplotlib.collections.PatchCollection(polys, alpha=COVER_ALPHA)
        ax.add_collection(col)

def rot(a, x=None):
    if x == None: x = (1, 0)
    x = np.matrix(x).T
    R = np.matrix([[np.cos(a), -np.sin(a)], [np.sin(a), np.cos(a)]])
    rx = R*x
    return (rx[0, 0], rx[1, 0])

def add(x, y):
    return (x[0] + y[0], x[1] + y[1])

def show():
    plt.subplots_adjust(left=0.001, right=0.999, top=0.999, bottom=0.001)
    plt.axis('equal')
    plt.show()

def draw():
    plt.subplots_adjust(left=0.001, right=0.999, top=0.999, bottom=0.001)
    plt.axis('equal')
    plt.draw()

def cover_area(ps, radius):
    u = shapely.ops.cascaded_union(
        [shapely.geometry.Point(p).buffer(radius) for p in ps])
    return u.area


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
        maxi, maxval = max(mgain.iteritems(), key=lambda x: x[1])
        perm.append(maxi)
        gains.append(maxval - totalarea)
        totalarea = maxval
        u = u.union(ps[maxi])
        del ps[maxi]
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
