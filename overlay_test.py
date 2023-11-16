import unittest
import overlay as o
import stellar_network as sn
import stellarbeat as sb
import z3

class OverlayTest(unittest.TestCase):
    def test_1(self):
        network = sn.StellarNetwork.from_json(
            [{'publicKey' : 'A', 'quorumSet' : {'threshold' : 1, 'validators' : ['A'], 'innerQuorumSets' : []}}])
        o.optimal(network)
        
    def test_2(self):
        qset = {'threshold' : 3, 'validators' : ['A','B','C'], 'innerQuorumSets' : 
                [{'threshold' : 2, 'validators' : ['1','2','3'], 'innerQuorumSets' : []}]}
        network = sn.StellarNetwork.from_json(
            [{'publicKey' : v, 'quorumSet' : qset} for v in ['A','B','C','1','2','3']])
        o.optimal(network)

    def test_3(self):
        network = sn.StellarNetwork.symmetric_network(4)
        # network.simplify_keys()
        o.optimal(network)

    @unittest.skip("takes too long")
    def test_4(self):
        network = sb.get_stellar_network().top_tier_only()
        network.simplify_keys()
        print(len(network.validators))
        o.optimal(network)