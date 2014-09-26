import pyor


def get_path(fin, source, target, ebr, tlim):
    path = pyor.get_path(fin,
                         source,
                         target,
                         eb_ratio=ebr,
                         time_limit=tlim,
                         plot=False,
                         verbose=False)
    return path
