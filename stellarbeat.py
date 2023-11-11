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

def get_stellar_network(update=False):
    return sn.StellarNetwork(get_validators(update=update))