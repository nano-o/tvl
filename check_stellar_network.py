# get json data from https://api.stellarbeat.io/v1/node-snapshots

import requests
import json
import itertools
import pysmt.shortcuts as ps
import three_valued as tv

url = "https://api.stellarbeat.io/v1/node"

def write_network_config(url):
    """
    Get data from stellarbeat and write network config (nodes and their qsets) to files nodes.json and validators.json
    """
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json() 
        # print(type(data))
        with open("nodes.json", "w") as outfile:
            json.dump(data, outfile)
        filtered_data = [{'publicKey': node['publicKey'], 'quorumSet': node['quorumSet']}
            for node in data if node['isValidator'] == True]
        print("There are {} validators".format
            (len(filtered_data)))
        with open("validators.json", "w") as outfile:
            json.dump(filtered_data, outfile)
    else:
        print("Error: Could not retrieve data from URL")

# load data from validators.json
with open("validators.json", "r") as infile:
    validators = json.load(infile)

validator_keys = set([node['publicKey'] for node in validators])
# print(validators)

def check_validators():
    """
    Check if all validators appearing in qsets are in the set of validators,
    that they all have a non-empty quorumSet, and that there is at most one level of nesting among quorumSets.
    """
    def check(json_data, pk):
        if isinstance(json_data, dict):
            for key, value in json_data.items():
                if key == 'validators':
                    for validator in value:
                        if validator not in validator_keys:
                            print("Unknown validator: {}".format(validator))
                elif key == 'quorumSet':
                    if not value:
                        print("Validator {} has an empty quorumSet".format(pk))
                elif key == 'innerQuorumSets':
                    for innerQuorumSet in value:
                        if innerQuorumSet['innerQuorumSets']:
                            print("An innerQuorumSet of validator {} has a nested innerQuorumSet".format(pk))
                check(value, pk)
        elif isinstance(json_data, list):
            for item in json_data:
                check(item, pk)
        else:
            return

    for validator in validators:
        check(validator, validator['publicKey'])
    
check_validators()

# now we need to build the closedAx formula

# we need to associate a symbol with each validator and each quorumset
# but pySMT already does memoization, so we don't need to do it ourselves
# for innerQuorumSets we can create symbols using their hash
def symbol(x):
    if type(x) == str:
        return ps.Symbol(x)
    else:
        return ps.Symbol(str(hash(str(x))))

def And(*args):
    assert len(args) > 0
    if len(args) > 2:
        return tv.And(args[0], And(*args[1:]))
    elif len(args) > 1:
        return tv.And(args[0],args[1])
    else: 
        return args[0]

def Or(*args):
    assert len(args) > 0
    if len(args) > 2:
        return tv.Or(args[0], Or(*args[1:]))
    elif len(args) > 1:
        return tv.Or(args[0],args[1])
    else: 
        return args[0]

def closed_ax_sym(sym, threshold, validators, innerQuorumSets):
    elems = validators + innerQuorumSets
    witnesses = list(itertools.combinations(elems, threshold))
    def witness_to_disj(witness):
        return Or(*[symbol(elem) for elem in witness])
    closed_ax_pos = tv.Dimp(And(*[witness_to_disj(witness) for witness in witnesses]), sym)
    def witness_to_disj_neg(witness):
        return Or(*[tv.Not(symbol(elem)) for elem in witness])
    closed_ax_neg = tv.Dimp(And(*[witness_to_disj_neg(witness) for witness in witnesses]), tv.Not(sym))
    return [closed_ax_pos, closed_ax_neg]

def closed_ax_innerqset(qset):
    return closed_ax_sym(symbol(qset), qset['threshold'], qset['validators'], qset['innerQuorumSets']) \
        + list(itertools.chain.from_iterable([closed_ax_innerqset(innerQset) for innerQset in qset['innerQuorumSets']]))

def closed_ax_validator(validator):
    return closed_ax_sym(symbol(validator['publicKey']), validator['quorumSet']['threshold'], validator['quorumSet']['validators'], validator['quorumSet']['innerQuorumSets']) \
        + list(itertools.chain.from_iterable([closed_ax_innerqset(innerQset) for innerQset in validator['quorumSet']['innerQuorumSets']]))

def closed_ax():
    return And(*list(itertools.chain.from_iterable([closed_ax_validator(validator) for validator in validators])))

axioms = closed_ax()

translation = tv.translate_for_satisfiability(axioms)
print(ps.is_sat(translation))