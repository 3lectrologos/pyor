import os.path
import pickle
import math
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import mip
import util


DATA_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data')
ROBO_FILE = os.path.join(DATA_DIR, 'samples_0.txt')

def create_graph():
    g = util.RoboGraph(ROBO_FILE)
    return g

def plot_graph(g, s, t, path=[], cover=False):
    plt.clf()
    g.plot()
    g.plot_path(path)
    g.plot_st(s, t)
    if cover:
        g.plot_cover()
    util.show()    

def get_path(s, t, node_budget=10, edge_budget=20, time_limit=10,
             plot=False, verbose=False):
    g = create_graph()
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
