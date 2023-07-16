# get json data from https://api.stellarbeat.io/v1/node-snapshots

import requests
import json
import stellar_network as sn

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

def get_validators():
    """
    Load data from validatos.json if possible, and otherwise from stellarbeat
    """
    try:
        with open('validators.json', 'r') as f:
            validators = json.load(f)
    except FileNotFoundError:
        validators = get_config_from_stellarbeat()
        with open('validators.json', 'w') as f:
            json.dump(validators, f)
    return validators
    
stellar_network = sn.StellarNetwork(get_validators())
print("There are {} validators".format(len(stellar_network.validators)))
print("There are {} different qsets:".format(len(stellar_network.qsets)))
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