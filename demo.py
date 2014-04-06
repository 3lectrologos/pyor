import math
import networkx as nx
import matplotlib.pyplot as plt
import mip
import util


def update_weights(g, path):
    rad = 0.0005
    f = lambda x: util.cover_area([g.pos[p] for p in x], rad)/(math.pi*rad**2)
    path_photo_nodes =  list(set(path) & set(g.photo_nodes()))
    sg = util.subg(f, g.photo_nodes(), path_photo_nodes)
    weights = {}
    for i in g.photo_nodes():
        weights[i] = sg([i])
    nx.set_node_attributes(g, 'w', weights)    

photo_locs = util.read_photo_locations('photo_coords.csv')
g = util.OsmGraph('roads_large.json')
g.add_photo_nodes(photo_locs)

plt.ion()
g.plot()
util.plot_cover(photo_locs)
util.draw()
#util.show()
(status, objective, path) = mip.find_path(g,
                                          start=2515,
                                          end=42,
                                          edge_budget=4000,
                                          node_budget=10)
update_weights(g, path)
plt.clf()
g.plot()
g.plot_path(path)
util.draw()
plt.gcf().set_size_inches(32, 18)
plt.savefig('init.pdf', format='pdf', bbox_inches='tight')
#util.show()
for niter in range(10):
    (status, objective, path) = mip.find_path(g,
                                              start=2515,
                                              end=42,
                                              edge_budget=3500,
                                              node_budget=10)

    print (status, objective, path)
    update_weights(g, path)
    plt.clf()
    g.plot()
    g.plot_path(path)
    util.draw()
    plt.gcf().set_size_inches(32, 18)
    plt.savefig('fig_' + str(niter) + '.pdf', format='pdf', bbox_inches='tight')
    #util.show()

#print 'covered area =', util.cover_area(path_photo_nodes)
#util.plot_cover(path_photo_nodes)
util.show()
