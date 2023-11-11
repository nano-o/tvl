from dataclasses import dataclass
import json
import itertools

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
    :ivar qsets: the set of all quorumSets in the network
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
            
    def simplify_keys(self):
        """
        Map the keys to numbers between 1 and n, represented as strings, where n is the number of validators.
        """
        def map_qset(qset):
            return QSet(qset.threshold,
                        frozenset([key_map[validator] for validator in qset.validators]),
                        frozenset([map_qset(innerQset) for innerQset in qset.innerQuorumSets]))
        keys = list(self.validators.keys())
        key_map = dict([(keys[i], str(i+1)) for i in range(len(keys))])
        self.validators = dict([(key_map[key], map_qset(qset)) for key,qset in self.validators.items()])
        self.sanity_check()
        self.qsets = set(self.validators.values())
    
    def to_dict(self):
        def qset_to_dict(qset):
            return {'threshold' : qset.threshold,
                    'validators' : list(qset.validators),
                    'innerQuorumSets' : [qset_to_dict(innerQset) for innerQset in qset.innerQuorumSets]}
        return [{'publicKey': pk, 'quorumSet': qset_to_dict(qset)} for pk,qset in self.validators.items()]

    def __str__(self) -> str:
        return json.dumps(self.to_dict(), indent=4)
    
def cartesian_product(sets):
    """
    Return the cartesian product of the given sets.
    """
    if len(sets) == 0:
        return frozenset([frozenset()])
    else:
        return frozenset([frozenset([e]) | s for e in sets[0] for s in cartesian_product(sets[1:])])
    
def union(sets):
    """
    Return the union of the given sets.
    """
    return frozenset(itertools.chain(*sets))
    
def blocking(qset):
    """
    Return the set of validators that are blocking for the given qset.
    """
    elems = qset.validators | qset.innerQuorumSets
    # enumerate all subsets of elems of size len(elems)-threshold+1:
    sets = itertools.combinations(elems, len(elems)-qset.threshold+1)
    # for each set, group the validators in a set and apply blocking to each qset:
    sets2 = frozenset([frozenset([e for e in s if isinstance(e, str)]) | frozenset([blocking(e) for e in s if isinstance(e, QSet)]) for s in sets])
    # for each set in sets2, take the product of its members:
    return frozenset([frozenset(itertools.chain(*s)) for s in sets2])

    # TODO