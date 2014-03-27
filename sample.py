import networkx as nx
import pylab as plt
import csv
import mip

geofile = 'data/valid_list-images-geo.tsv'
fout = 'tmp.csv'
edgefile = 'data/graph-pruned_min=0.1_max=0.2.tsv'

key = dict()
g = nx.Graph()

with open(geofile, 'r') as tsvin, open(fout, 'w') as csvout:
    tsvin = csv.reader(tsvin, delimiter='\t')
    csvout = csv.writer(csvout)
    csvout.writerow(['Longitude', 'Latitude'])
    for i, row in enumerate(tsvin):
        s = row[0] + '_' + row[1]
        pos = (float(row[3]), float(row[2]))
        key[s] = i
        g.add_node(i, w=1, pos=pos)
        csvout.writerow(pos)

with open(edgefile, 'r') as tsvin:
    tsvin = csv.reader(tsvin, delimiter='\t')
    for row in tsvin:
        g.add_edge(key[row[0]], key[row[1]], t=float(row[2]))

pos = nx.get_node_attributes(g, 'pos')
(status, objective, path) = mip.find_path(g, start=64, end=155, budget=2)
print 'Status: ', status
print 'Objective = ', objective
mip.plot_path(g, path, pos=pos)
