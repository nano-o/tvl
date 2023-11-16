# get json data from https://api.stellarbeat.io/v1/node-snapshots
import stellarbeat as sb
import stellar_network as sn
import sys
import tvl_checks as tvlc

# if no arguments were given, then load data from validators.json if possible, and otherwise from stellarbeat
# otherwise, if the first argument is '--update', then load data from stellarbeat and save it to validators.json
if len(sys.argv) > 1:
    if sys.argv[1] == '--update':
        stellar_network = sb.get_stellar_network(update=True)
    else:
        print("Usage: python3 check_stellar_network.py [--update]")
        sys.exit(1)
else:
    print("Loading data from validators.json. Use --update to get fresh data from stellarbeat.")
    stellar_network = sb.get_stellar_network()

print("There are {} validators".format(len(stellar_network.validators)))
print("There are {} different qsets".format(len(stellar_network.qsets())))

stellar_network.simplify_keys()
print(stellar_network)

# for qset in stellar_network.qsets:
#     print("{}\n".format(qset))

# import cProfile
# cProfile.run('stellar_network.check_network_intertwined()', 'restats')
# import pstats
# from pstats import SortKey
# p = pstats.Stats('restats')
# p.strip_dirs().sort_stats(SortKey.CUMULATIVE).print_stats(20)

# print("Is the Stellar network interwined? {}"
#       .format(tvlc.check_network_intertwined(stellar_network)))