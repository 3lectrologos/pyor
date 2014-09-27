import os
import pyor


fin = 'data.txt'

path = pyor.get_path(fin, 0, 1, eb_ratio=1.5, time_limit=1.0,
                     plot=False, verbose=False)

print 'path =', path
