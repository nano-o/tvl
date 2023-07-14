import itertools
import pysmt.shortcuts as ps
import three_valued_logic as tvl

"""
This file contains functions for checking whether a given network of validators (consisting of public keys and their quorumSets) is intertwined by reduction to SAT.

"""

class StellarNetwork:
    """
    A Stellar network is a list of validators, each of which is represented by their public key and has a quorumSet.

    :ivar validators: a dictionary mapping public keys to quorumSets
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
        self.validators = dict([(validator['publicKey'], validator['quorumSet']) for validator in validators])
        self.sanity_check()


    def sanity_check(self):
        """
        Perform a few sanity checks
        """
        def check_qset(qset):
            elems = qset['validators'] + qset['innerQuorumSets'] 
            if not elems:
                raise ValueError("Empty quorumSet")
            if qset['threshold'] > len(elems):
                raise ValueError("Threshold {} greater than number of elements in the qset ({})".format(qset['threshold'], len(elems)))
            if qset['threshold'] < 1:
                raise ValueError("Threshold {} less than 1".format(qset['threshold']))
            for key, value in qset.items():
                if key == 'validators':
                    for pk in value:
                        if pk not in self.validators:
                            raise ValueError("Unknown validator: {}".format(pk))
                elif key == 'innerQuorumSets':
                    for innerQuorumSet in value:
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
        return And(*itertools.chain.from_iterable([closed_ax_validator(validator, qset) for validator,qset in self.validators.items()]))
    
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
    Associate a symbol with a validator or a quorumSets.
    Hopefully, pySMT already does memoization, so we don't need to do it ourselves.
    For quorumSets, we create symbols using their hash.
    """
    if isinstance(x, str):
        return ps.Symbol("V:"+x)
    elif isinstance(x, dict):
        return ps.Symbol("Q:"+str(hash(str(x))))
    else:
        raise Exception("Wrong type of {} for a symbol: {}".format(x, type(x)))

def And(*args):
    assert len(args) > 0
    value = args[0]
    for f in args[1:]:
        value = tvl.And(f, value)
    return value
    
def Or(*args):
    assert len(args) > 0
    assert len(args) > 0
    value = args[0]
    for f in args[1:]:
        value = tvl.Or(f, value)
    return value

def closed_ax_sym(e, threshold, validators, innerQuorumSets):
    """
    :param e: a public key or an innerQuorumSet
    """
    elems = validators + innerQuorumSets
    witnesses = list(itertools.combinations(elems, threshold))
    def witness_to_disj(witness):
        return Or(*[symbol(elem) for elem in witness])
    closed_ax_pos = tvl.Dimp(And(*[witness_to_disj(witness) for witness in witnesses]), symbol(e))
    def witness_to_disj_neg(witness):
        return Or(*[tvl.Not(symbol(elem)) for elem in witness])
    closed_ax_neg = tvl.Dimp(And(*[witness_to_disj_neg(witness) for witness in witnesses]), tvl.Not(symbol(e)))
    return [closed_ax_pos, closed_ax_neg]

def closed_ax_innerqset(qset):
    assert isinstance(qset, dict)
    return closed_ax_sym(qset, qset['threshold'], qset['validators'], qset['innerQuorumSets']) \
        + list(itertools.chain.from_iterable([closed_ax_innerqset(innerQset) for innerQset in qset['innerQuorumSets']]))

def closed_ax_validator(validator, qset):
    assert isinstance(validator, str)
    assert isinstance(qset, dict)
    return closed_ax_sym(validator,
                            qset['threshold'],
                            qset['validators'],
                            qset['innerQuorumSets']) \
        + list(itertools.chain.from_iterable([closed_ax_innerqset(innerQset) for innerQset in qset['innerQuorumSets']]))

def intertwined(p, q):
    assert isinstance(p, str) and isinstance(q, str)
    return tvl.Or(tvl.And(symbol(p), symbol(q)),tvl.And(tvl.Not(symbol(p)),tvl.Not(symbol(q))))
