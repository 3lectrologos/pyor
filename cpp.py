import pyor


def get_path(fin, source, target, bedge, tlim):
    path = pyor.get_path(fin,
                         source,
                         target,
                         edge_budget=bedge,
                         time_limit=tlim,
                         plot=False,
                         verbose=False)
    return path
