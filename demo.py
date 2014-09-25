import os
import pyor


fin = 'data.txt'

path = pyor.get_path(fin, 0, 1, edge_budget=3.780, time_limit=3.0,
                     plot=False, verbose=False)
print 'path =', path
