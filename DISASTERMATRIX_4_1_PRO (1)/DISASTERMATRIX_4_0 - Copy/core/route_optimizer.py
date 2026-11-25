import networkx as nx

def build_demo_graph(blocked_edges=None, flood_penalty=1.0):
    blocked = {tuple(sorted(e)) for e in (blocked_edges or [])}
    g = nx.Graph()
    edges = [
        ("A","B",4),("B","C",3),("C","D",4),("E","F",3),("F","G",3),
        ("G","H",4),("I","J",4),("J","K",3),("K","L",3),
        ("M","N",3),("N","O",4),("O","P",3),("A","E",3),("E","I",4),
        ("I","M",3),("B","F",4),("F","J",3),("J","N",4),("C","G",3),
        ("G","K",4),("K","O",3),("D","H",3),("H","L",4),("L","P",3)
    ]
    for u,v,cost in edges:
        if tuple(sorted((u,v))) not in blocked:
            g.add_edge(u,v,weight=float(cost)*flood_penalty)
    return g

def shortest_route(start, destination, blocked_edges=None, flood_penalty=1.0):
    graph = build_demo_graph(blocked_edges, flood_penalty)
    try:
        path = nx.shortest_path(graph, start, destination, weight="weight", method="dijkstra")
        cost = nx.path_weight(graph, path, weight="weight")
        return {"path": path, "cost": round(cost,2), "segments": list(zip(path[:-1], path[1:]))}
    except (nx.NetworkXNoPath, nx.NodeNotFound):
        return {"path": [], "cost": None, "segments": []}
