import stellar_network as sn
import itertools
from z3 import *

def find_optimal_overlay(network):
    # first create a boolean variable for every pair of validators:
    validator_pairs = list(itertools.combinations(network.validators.keys(), 2))
    def edge(pair):
        return "v" + pair[0] + "v" + pair[1]
    edges = [Bool(edge(pair)) for pair in validator_pairs]

    def connected(v, qset):
        # assert that v is connected to each slice in the qset:
        return And([Or([Bool(edge((v, w))) for w in slice]) for slice in qset])
