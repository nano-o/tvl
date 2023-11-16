import stellar_network as sn
import itertools
from z3 import *

def edge(ab: frozenset) -> str:
    pair = tuple(sorted(ab))
    return pair[0] + "-" + pair[1]

def optimal(network):
    
    validator_pairs = [frozenset(p) for p in itertools.combinations(network.validators.keys(), 2)]
    # create a dict mapping each pair of validators to a corresponding boolean variable:
    edge_vars = {p: Bool(edge(p)) for p in validator_pairs}

    def slice_cover(v, qset):
        # assert that v has at least one connection to each slice in the qset
        # in other words, v is connected to at least one blocking set of the qset
        blocking_sets = [b for b in sn.blocking(qset) if v not in b] # TODO: is this correct?
        for b in blocking_sets:
            for w in b:
                assert w in network.validators.keys(), f"w = {w} not a validator"
        return Or([And([edge_vars[frozenset((v, w))] for w in blocking_set]) for blocking_set in blocking_sets])
    
    def slices_covered():
        return And([slice_cover(v, qset) for v, qset in network.validators.items()])
    
    def diameter_max_2():
        # assert that each pair of validators is connected by a path of length at most 2
        def distance_max_2(u,v):
            return Or(edge_vars[frozenset((u,v))],Or([And([edge_vars[frozenset((u,w))], edge_vars[frozenset((w,v))]]) for w in network.validators.keys() if w != u and w != v]))
        return And([distance_max_2(u,v) for u,v in [tuple(p) for p in validator_pairs]])

    o = z3.Optimize()
    o.add(diameter_max_2())
    o.add(slices_covered())
    for ne in [Not(edge_vars[p]) for p in validator_pairs]:
        o.add_soft(ne)
    print('solving')
    o.check()
    print(o.model())