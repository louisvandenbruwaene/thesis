"""Check the Step 4 torso bookkeeping on one graph, in all three temporary-connection cases."""
import networkx as nx, itertools
INF = 10**6
def kappa(G,s,t):
    D=nx.DiGraph()
    for v in G: D.add_edge((v,'i'),(v,'o'),capacity=1)
    for u,v in G.edges():
        D.add_edge((u,'o'),(v,'i'),capacity=1); D.add_edge((v,'o'),(u,'i'),capacity=1)
    return nx.maximum_flow_value(D,(s,'o'),(t,'i'))
def rank(G): return G.number_of_edges()-G.number_of_nodes()+1

base=[('a','u1'),('a','u2'),('b','u1'),('b','u2'),('u1','u2'),
      ('a','w1'),('a','w2'),('b','w1'),('b','w2'),('w1','w2')]

def report(name, extra, X, case):
    G=nx.Graph(base+extra)
    print(f'--- {name}: |V|={G.number_of_nodes()} |E|={G.number_of_edges()} rank={rank(G)} |X|-1={len(X)-1}')
    print('    min degree', min(dict(G.degree()).values()),
          '| 2-connected', nx.node_connectivity(G)==2,
          '| kappa>2 among X pairs:',
          [(u,v,kappa(G,u,v)) for u,v in itertools.combinations(sorted(X),2) if kappa(G,u,v)>2][:2])
    s=len({'a','b'}&set(X))
    tot=0
    for side in ('u','w'):
        keep=[side+'1',side+'2','a','b']
        T=nx.Graph([e for e in G.edges() if e[0] in keep and e[1] in keep])
        T.add_nodes_from(keep)
        if case==1: pass                                   # ab already retained
        elif case==2: T.add_edge('a','b')
        else: T.add_edge('t','a'); T.add_edge('t','b')
        XT=set(X)&set(T) | ({'t'} if case==3 else set())
        tot+=rank(T)
        print(f'    torso {side}: |V|={T.number_of_nodes()} |E|={T.number_of_edges()} '
              f'rank={rank(T)} |X_T|={len(XT)} smaller={(T.number_of_nodes()+T.number_of_edges())<(G.number_of_nodes()+G.number_of_edges())}')
    pred = tot if case==1 else tot-1
    print(f'    predicted rank(G) = {pred}, actual {rank(G)}  ->', pred==rank(G))
    print(f'    |X_U|+|X_W| predicted {len(X)+(1 if case==1 else (s if case==2 else 2))}')

report('case 2  (ab not an edge, s=2)', [], {'a','b','u2','w2'}, 2)
report('case 1  (ab an edge, s=1)', [('a','b')], {'a','u1','u2','w1','w2'}, 1)
report('case 3  (ab not an edge, s=0)', [], {'u1','u2','w1','w2'}, 3)
