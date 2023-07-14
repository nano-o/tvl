# get json data from https://api.stellarbeat.io/v1/node-snapshots

import requests
import json
import itertools
import pysmt.shortcuts as ps
import three_valued_logic as tlv
import stellar_network as sn

url = "https://api.stellarbeat.io/v1/node"

def write_stellarbeat_config(url):
    """
    Get data from stellarbeat and write network config (nodes and their qsets) to files nodes.json and validators.json
    """
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json() 
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

stellar_network = sn.StellarNetwork(validators)

import sys
sys.setrecursionlimit(10000)

print("Is the Stellar network interwined? {}".format(stellar_network.check_network_intertwined()))