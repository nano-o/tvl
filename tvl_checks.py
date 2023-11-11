import itertools
import pysmt.shortcuts as ps
import three_valued_logic as tvl
import stellar_network as sn
from dataclasses import dataclass

"""
This file contains functions for checking whether a given network of validators (consisting of public keys and their quorumSets) is intertwined by reduction to SAT.
"""

def closed_ax(network):
    """
    Return the closedAx formula as computed from the quorumSets of the validators.
    TODO: Check this is still accurate according to three.pdf
    """

    lhs_cache = dict()
    closed_ax_fmlas = []

    def add_closed_ax(validator_or_qset, qset):
        """
        Add the closure axioms for the given qset to the list closed_ax.

        :param qset: a QSet
        :param variable: a pysmt symbol
        """
        if isinstance(validator_or_qset, sn.QSet) and qset in lhs_cache:
            pass
        elif isinstance(validator_or_qset, str) and qset in lhs_cache:
            assert len(lhs_cache[qset]) == 2
            closed_ax_pos = tvl.Dimp(lhs_cache[qset][0], symbol(validator_or_qset))
            closed_ax_neg = tvl.Dimp(lhs_cache[qset][1], tvl.Not(symbol(validator_or_qset)))
            closed_ax_fmlas.extend([closed_ax_pos,closed_ax_neg])
        else:
            elems = qset.validators | qset.innerQuorumSets
            witnesses = list(itertools.combinations(elems, qset.threshold))
            def witness_to_disj_pos(witness):
                return Or(*[symbol(e) for e in witness])
            lhs_pos = And(*[witness_to_disj_pos(w) for w in witnesses])
            closed_ax_pos = tvl.Dimp(lhs_pos, symbol(validator_or_qset))
            def witness_to_disj_neg(witness):
                return Or(*[tvl.Not(symbol(e)) for e in witness])
            lhs_neg = And(*[witness_to_disj_neg(w) for w in witnesses])
            closed_ax_neg = tvl.Dimp(lhs_neg, tvl.Not(symbol(validator_or_qset)))
            lhs_cache[qset] = [lhs_pos, lhs_neg]
            closed_ax_fmlas.extend([closed_ax_pos,closed_ax_neg])
            for innerQset in qset.innerQuorumSets:
                add_closed_ax(innerQset, innerQset)

    for v,qset in network.validators.items():
        add_closed_ax(v, qset)

    return And(*closed_ax_fmlas)

def is_intertwined(network):
    if len(network.validators) == 1:
        return tvl.Not(tvl.F)
    else:
        return tvl.Dimp(closed_ax(network), And(*[intertwined(p, q) for [p,q] in itertools.combinations(network.validators.keys(), 2)]))
    
def check_intertwined(network, p, q):
    return tvl.is_valid(tvl.Dimp(closed_ax(network), intertwined(p,q)))
    
def check_network_intertwined(network):
    return tvl.is_valid(is_intertwined(network))

def symbol(x):
    """
    Associate a symbol with a validator or a QSet.
    Hopefully, pySMT already does memoization, so we don't need to do it ourselves.
    """
    assert isinstance(x, str) or isinstance(x, sn.QSet)
    return ps.Symbol(str(hash(x)))

def And(*args):
    assert len(args) > 0
    value = args[0]
    for f in args[1:]:
        value = tvl.And(f, value)
    return value
    
def Or(*args):
    assert len(args) > 0
    value = args[0]
    for f in args[1:]:
        value = tvl.Or(f, value)
    return value

def intertwined(p, q):
    assert isinstance(p, str) and isinstance(q, str)
    return tvl.Or(tvl.And(symbol(p), symbol(q)),tvl.And(tvl.Not(symbol(p)),tvl.Not(symbol(q))))