# get json data from https://api.stellarbeat.io/v1/node-snapshots

import requests
import json
import stellar_network as sn
import sys

def get_config_from_stellarbeat():
    """
    Get data from stellarbeat, filter it, and return it as a list of dictionaries
    """
    url = "https://api.stellarbeat.io/v1/node"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        filtered_data = [{'publicKey': node['publicKey'], 'quorumSet': node['quorumSet']}
            for node in data if node['isValidator'] == True]
        return filtered_data
    else:
        print("Error: Could not retrieve data from URL")

def get_validators(update=False):
    """
    If update is False, loads data from validatos.json if possible, and otherwise from stellarbeat.
    Otherwise, loads data from stellarbeat and saves it to validators.json
    """
    if update:
        print("Updating validators.json")
        validators = get_config_from_stellarbeat()
        with open('validators.json', 'w') as f:
            json.dump(validators, f)
    else:
        try:
            with open('validators.json', 'r') as f:
                validators = json.load(f)
        except FileNotFoundError:
            validators = get_config_from_stellarbeat()
            with open('validators.json', 'w') as f:
                json.dump(validators, f)
    return validators

# if no arguments were given, then load data from validators.json if possible, and otherwise from stellarbeat
# otherwise, if the first argument is '--update', then load data from stellarbeat and save it to validators.json
if len(sys.argv) > 1:
    if sys.argv[1] == '--update':
        validators = get_validators(update=True)
    else:
        print("Usage: python3 check_stellar_network.py [--update]")
        sys.exit(1)
else:
    print("Loading data from validators.json. Use --update to get fresh data from stellarbeat.")
    validators = get_validators()

stellar_network = sn.StellarNetwork(validators)
print("There are {} validators".format(len(stellar_network.validators)))
print("There are {} different qsets".format(len(stellar_network.qsets)))
# for qset in stellar_network.qsets:
#     print("{}\n".format(qset))

# import cProfile
# cProfile.run('stellar_network.check_network_intertwined()', 'restats')
# import pstats
# from pstats import SortKey
# p = pstats.Stats('restats')
# p.strip_dirs().sort_stats(SortKey.CUMULATIVE).print_stats(20)

print("Is the Stellar network interwined? {}"
      .format(stellar_network.check_network_intertwined()))