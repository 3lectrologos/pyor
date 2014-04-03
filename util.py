import networkx as nx

def get_photo_nodes(g):
    return [v[0] for v in g.nodes(data=True)
            if v[1].has_key('photo') and v[1]['photo'] == True]
