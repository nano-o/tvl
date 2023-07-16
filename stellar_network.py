import itertools
import pysmt.shortcuts as ps
import three_valued_logic as tvl
import json
from dataclasses import dataclass

"""
This file contains functions for checking whether a given network of validators (consisting of public keys and their quorumSets) is intertwined by reduction to SAT.
"""

@dataclass(frozen=True)
class QSet:
    """
    A quorumSet. Can be used as a key in a dictionary and as an element in a set.
    """
    threshold: int
    validators: frozenset[str]
    innerQuorumSets: frozenset

    @staticmethod
    def from_json(json_qset):
        """
        :param json_qset: a dictionary representing the quorumSet
        """
        return QSet(json_qset['threshold'],
                    frozenset(json_qset['validators']),
                    frozenset([QSet.from_json(qset) for qset in json_qset['innerQuorumSets']]))

class StellarNetwork:
    """
    A Stellar network is a list of validators, each of which is represented by their public key and has a quorumSet.

    :ivar validators: a dictionary mapping public keys to quorumSets
    :ivar qset: the set of all quorumSets in the network
    """

    def __init__(self, validators):
        """
         :param validators: list of dictionaries, each of which describes a validator; and has the following form:

        .. code-block:: python

            {'publicKey' : 'GABCD...', 
            'quorumSet' : {
                'threshold' : 3, 
                'validators' : ['GABCD...', 'GABCDE...', ...], 
                'innerQuorumSets' : [
                    {'threshold' : 2, 
                    'validators' : ['GABCD...', 'GABCDE...', ...], 
                    'innerQuorumSets' : [...]},
                    ...]}}
        """
        # check that no validator appears twice:
        if len(validators) != len(set([validator['publicKey'] for validator in validators])):
            raise ValueError("Duplicate validator")
        # create a dictionary mapping public keys to QSets:
        self.validators = dict(
            [(validator['publicKey'], QSet.from_json(validator['quorumSet'])) for validator in validators])
        self.sanity_check()
        self.qsets = set(self.validators.values())

    def sanity_check(self):
        """
        Perform a few sanity checks
        """
        def check_qset(qset: QSet):
            # if both validators and innerQuorumSets are empty, then raise an error:
            if not qset.validators and not qset.innerQuorumSets:
                raise ValueError("Empty quorumSet")
            elems = qset.validators | qset.innerQuorumSets
            if qset.threshold > len(elems):
                raise ValueError(
                    "Threshold {} greater than number of elements in the qset ({})"
                    .format(qset.threshold, len(elems)))
            if qset.threshold < 1:
                raise ValueError("Threshold {} less than 1".format(qset.threshold))
            for pk in qset.validators:
                    if pk not in self.validators:
                        raise ValueError("Unknown validator: {}".format(pk))
            for innerQuorumSet in qset.innerQuorumSets:
                    check_qset(innerQuorumSet)

        for pk,qset in self.validators.items():
            try:
                check_qset(qset)
            except ValueError as e:
                raise ValueError("Error in validator {}: {}".format(pk, e))

    def closed_ax(self):
        """
        Return the closedAx formula as computed from the quorumSets of the validators.
        """

        lhs_cache = dict()
        closed_ax_fmlas = []
    
        def add_closed_ax(validator_or_qset, qset):
            """
            Add the closure axioms for the given qset to the list closed_ax.

            :param qset: a QSet
            :param variable: a pysmt symbol
            """
            if isinstance(validator_or_qset, QSet) and qset in lhs_cache:
                pass
            elif isinstance(validator_or_qset, str) and qset in lhs_cache:
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

        for v,qset in self.validators.items():
            add_closed_ax(v, qset)

        return And(*closed_ax_fmlas)

    def network_intertwined(self):
        if len(self.validators) == 1:
            return tvl.Not(tvl.F)
        else:
            return tvl.Dimp(self.closed_ax(), And(*[intertwined(p, q) for [p,q] in itertools.combinations(self.validators.keys(), 2)]))
        
    def check_intertwined(self, p, q):
        return tvl.is_valid(tvl.Dimp(self.closed_ax(), intertwined(p,q)))
        
    def check_network_intertwined(self):
        return tvl.is_valid(self.network_intertwined())

def symbol(x):
    """
    Associate a symbol with a validator or a QSet.
    Hopefully, pySMT already does memoization, so we don't need to do it ourselves.
    """
    assert isinstance(x, str) or isinstance(x, QSet)
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
