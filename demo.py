import os
import pyor


fin = 'data.txt'

path = pyor.get_path(fin, 0, 142, eb_ratio=1.5, time_limit=3.0,
                     plot=False, verbose=False)

print 'path =', path
