import os.path
import pickle
import math
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import mip
import util


def create_graph(fin):
    g = util.RoboGraph(fin)
    return g

def plot_graph(g, s, t, path=[], cover=False):
    plt.clf()
    g.plot()
    g.plot_path(path)
    g.plot_st(s, t)
    if cover:
        g.plot_cover()
    util.show()    

def get_path(fin, s, t, node_budget=10, edge_budget=20, time_limit=10,
             plot=False, verbose=False):
    g = create_graph(fin)
    if plot:
        plot_graph(g, s, t, cover=True)
    (status, objective, path) = mip.find_path(g,
                                              start=s,
                                              end=t,
                                              edge_budget=edge_budget,
                                              node_budget=node_budget,
                                              time_limit=time_limit,
                                              verbose=verbose)
    if plot:
        plot_graph(g, s, t, path=path, cover=False)
    return path
