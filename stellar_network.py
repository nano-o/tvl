from dataclasses import dataclass
import json
import itertools
from typing import List, Iterable
import math

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
    
    def members(self) -> frozenset[str]:
        """
        Return the set of members of the quorumSet.
        """
        return self.validators | union([innerQset.members() for innerQset in self.innerQuorumSets])

class StellarNetwork:
    """
    A Stellar network is a list of validators, each of which is represented by their public key and has a quorumSet.

    :ivar validators: a dictionary mapping public keys to quorumSets
    """

    def top_tier(self):
        return self.most_frequent_qset().members() 

    def __init__(self, validators: dict[str, QSet]):
        """
        :param validators: a dictionary mapping public keys to quorumSets
        """
        self.validators = validators
        self.sanity_check()


    @staticmethod
    def symmetric_network(norgs):
        """
        Return a symmetric network with norgs organizations and org threshold 2/3, with each org running 3 validators with a threshold of 2.
        """
        orgs = [f"org{i}" for i in range(norgs)]
        validators = [f"{org}v{i}" for org in orgs for i in range(3)]
        threshold = math.floor(2*norgs//3)+1
        innerQsets = [{'threshold' : 2, 'validators' : [validators[3*i+j] for j in range(3)], 'innerQuorumSets' : []} for i in range(norgs)]
        qset = QSet.from_json({'threshold' : threshold, 'validators' : [], 'innerQuorumSets' : innerQsets})
        return StellarNetwork({v:qset for v in validators})

    @staticmethod
    def from_json(validators):
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
        validators = dict(
            [(validator['publicKey'], QSet.from_json(validator['quorumSet'])) for validator in validators])
        return StellarNetwork(validators)
        
    def qsets(self):
        return self.validators.values()

    def most_frequent_qset(self) -> QSet:
        """
        Return the most frequent qset in the network.
        """
        return max(self.qsets(), key=lambda qset: len([q for q in self.validators.values() if q == qset]))
    
    def top_tier_only(self):
        """
        Return a new StellarNetwork object that only contains the top tier validators.
        """
        top_tier_validators = {pk:qset for pk,qset in self.validators.items() if pk in self.top_tier()}
        return StellarNetwork(top_tier_validators)

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
        Updates the object in place.
        """
        def map_qset(qset):
            return QSet(qset.threshold,
                        frozenset([key_map[validator] for validator in qset.validators]),
                        frozenset([map_qset(innerQset) for innerQset in qset.innerQuorumSets]))
        keys = list(self.validators.keys())
        key_map = dict([(keys[i], str(i+1)) for i in range(len(keys))])
        self.validators = dict([(key_map[key], map_qset(qset)) for key,qset in self.validators.items()])
        self.sanity_check()
    
    def to_dict(self):
        def qset_to_dict(qset):
            return {'threshold' : qset.threshold,
                    'validators' : list(qset.validators),
                    'innerQuorumSets' : [qset_to_dict(innerQset) for innerQset in qset.innerQuorumSets]}
        return [{'publicKey': pk, 'quorumSet': qset_to_dict(qset)} for pk,qset in self.validators.items()]

    def __str__(self) -> str:
        return json.dumps(self.to_dict(), indent=4)
    
def one_of_each(list_of_sets:List[frozenset[frozenset[str]]]) -> frozenset[frozenset[str]]:
    """
    Returns all the sets that can be formed by picking one set in each set in the list and taking their union.
    """
    if len(list_of_sets) == 0:
        return frozenset() # TODO or frozenset(frozenset()) ?
    elif len(list_of_sets) == 1:
        return frozenset(list_of_sets[0])
    else:
        head = list_of_sets[0]
        tail = list_of_sets[1:]
        tail_prod = one_of_each(tail) # set of sets
        return frozenset([e | s for e in head for s in tail_prod])

def union(sets:Iterable[frozenset]) -> frozenset:
    """
    Return the union of the given sets.
    """
    return frozenset(itertools.chain(*sets))

def expand_combination(c) -> frozenset[frozenset[str]]:
    list_of_sets_of_sets = [frozenset([frozenset([e])]) if isinstance(e, str) else blocking(e) for e in c]
    return one_of_each(list_of_sets_of_sets)
    
def blocking(qset:QSet) -> frozenset[frozenset[str]]:
    """
    Return the set of validators that are minimally blocking for the given qset.
    """
    elems = qset.validators | qset.innerQuorumSets
    # enumerate all subsets of elems of size len(elems)-threshold+1:
    combinations = itertools.combinations(elems, len(elems)-qset.threshold+1)

    res = union(frozenset([expand_combination(c) for c in combinations]))
    for b in res:
        assert b.issubset(qset.members()), f"{pretty_print_frozenset(b)} not a subset of qset.members() = {pretty_print_frozenset(qset.members())}"
    return res

def pretty_print_frozenset(fset):
    """
    Pretty print a frozenset
    """
    return "{" + ", ".join([pretty_print_frozenset(e) if isinstance(e, frozenset) else str(e) for e in fset]) + "}"