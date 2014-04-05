import matplotlib.pyplot as plt
import mip
import util


photo_locs = util.read_photo_locations('photo_coords.csv')
g = util.OsmGraph('roads_large.json')
g.add_photo_nodes(photo_locs)
(status, objective, path) = mip.find_path(g, start=2515, end=42, budget=3500,
                                          minnodes=5, maxnodes=10)
print (status, objective, path)
g.plot()
g.plot_path(path)
util.show()
