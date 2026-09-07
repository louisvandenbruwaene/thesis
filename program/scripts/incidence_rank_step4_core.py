"""Search for a graph that Step 4 of lem:incidence-rank actually has to handle:
2-connected, simple, minimum degree >= 3, NOT 3-connected, carrying a partition
V = X u Z with Z independent and kappa(x,x') <= 2 for every pair inside X."""
import itertools, subprocess, sys
import networkx as nx

INF = 10**6

def kappa(G, s, t):
    """Max number of internally disjoint s-t paths (a direct edge counts as one).

    Interior vertices carry capacity 1 and every arc carries capacity 1, so the
    direct s-t arc, which bypasses every vertex split, contributes exactly one.
    """
    D = nx.DiGraph()
    for v in G:
        D.add_edge((v, 'in'), (v, 'out'), capacity=1)
    for u, v in G.edges():
        D.add_edge((u, 'out'), (v, 'in'), capacity=1)
        D.add_edge((v, 'out'), (u, 'in'), capacity=1)
    return nx.maximum_flow_value(D, (s, 'out'), (t, 'in'))

def partitions(G):
    """Independent sets Z (possibly empty) whose complement X caps kappa at 2."""
    V = list(G)
    cap = {}
    for x, y in itertools.combinations(V, 2):
        cap[frozenset((x, y))] = kappa(G, x, y)
    for size in range(len(V) - 2, -1, -1):
        for Z in itertools.combinations(V, size):
            Zs = set(Z)
            if any(G.has_edge(u, v) for u, v in itertools.combinations(Z, 2)):
                continue
            X = [v for v in V if v not in Zs]
            if len(X) < 3 and Zs:
                continue
            if all(cap[frozenset((x, y))] <= 2 for x, y in itertools.combinations(X, 2)):
                yield Zs, X

def search(n):
    out = subprocess.run(['geng', '-q', '-c', '-d3', str(n)],
                         capture_output=True, text=True).stdout.split()
    kept = 0
    for g6 in out:
        G = nx.from_graph6_bytes(g6.encode())
        if nx.node_connectivity(G) != 2:      # 2-connected but not 3-connected
            continue
        kept += 1
        for Z, X in partitions(G):
            rank = G.number_of_edges() - G.number_of_nodes() + 1
            return dict(g6=g6, Z=sorted(Z), X=sorted(X), rank=rank,
                        bound=len(X) - 1, candidates=kept, total=len(out))
    return dict(g6=None, candidates=kept, total=len(out))

if __name__ == "__main__":
  for n in range(5, int(sys.argv[1]) + 1):
      r = search(n)
      print(n, r, flush=True)
