import stellar_network as sn
import tvl_checks as tvlc
import unittest

class TestTVLChecks(unittest.TestCase):
    def test_1(self):
        network = sn.StellarNetwork(
            [{'publicKey' : 'A', 'quorumSet' : {'threshold' : 1, 'validators' : ['A'], 'innerQuorumSets' : []}}])
        self.assertTrue(tvlc.check_network_intertwined(network))

    def test_2(self):
        network = sn.StellarNetwork(
            [{'publicKey' : 'A', 'quorumSet' : {'threshold' : 1, 'validators' : ['B'], 'innerQuorumSets' : []}},
             {'publicKey' : 'B', 'quorumSet' : {'threshold' : 1, 'validators' : ['A'], 'innerQuorumSets' : []}}])
        formula = tvlc.is_intertwined(network)
        # write the formula to the file log.txt:
        with open('log.txt', 'w') as f:
            f.write(formula.serialize())
        self.assertTrue(tvlc.check_network_intertwined(network))

    def test_3(self):
        network = sn.StellarNetwork(
            [{'publicKey' : 'A', 'quorumSet' : {'threshold' : 1, 'validators' : ['B'], 'innerQuorumSets' : []}},
             {'publicKey' : 'B', 'quorumSet' : {'threshold' : 1, 'validators' : ['B'], 'innerQuorumSets' : []}}])
        self.assertTrue(tvlc.check_network_intertwined(network))

    def test_4(self):
        network = sn.StellarNetwork(
            [{'publicKey' : 'A', 'quorumSet' : {'threshold' : 1, 'validators' : ['A'], 'innerQuorumSets' : []}},
             {'publicKey' : 'B', 'quorumSet' : {'threshold' : 1, 'validators' : ['B'], 'innerQuorumSets' : []}}])
        self.assertFalse(tvlc.check_network_intertwined(network))

    def test_5(self):
        network = sn.StellarNetwork(
            [{'publicKey' : 'A', 'quorumSet' : {'threshold' : 1, 'validators' : ['B'], 'innerQuorumSets' : []}},
             {'publicKey' : 'B', 'quorumSet' : {'threshold' : 1, 'validators' : ['C'], 'innerQuorumSets' : []}},
             {'publicKey' : 'C', 'quorumSet' : {'threshold' : 1, 'validators' : ['A'], 'innerQuorumSets' : []}}])
        self.assertTrue(tvlc.check_network_intertwined(network))

    def test_6(self):
        network = sn.StellarNetwork(
            [{'publicKey' : 'A', 'quorumSet' : {'threshold' : 1, 'validators' : ['B'], 'innerQuorumSets' : []}},
             {'publicKey' : 'B', 'quorumSet' : {'threshold' : 1, 'validators' : ['A'], 'innerQuorumSets' : []}},
             {'publicKey' : 'C', 'quorumSet' : {'threshold' : 1, 'validators' : ['B','D'], 'innerQuorumSets' : []}},
             {'publicKey' : 'D', 'quorumSet' : {'threshold' : 1, 'validators' : ['A','D'], 'innerQuorumSets' : []}}])
        self.assertFalse(tvlc.check_network_intertwined(network))
        self.assertTrue(tvlc.check_intertwined(network,'A','B'))
        self.assertFalse(tvlc.check_intertwined(network,'A','C'))

    def test_7(self):
        network = sn.StellarNetwork(
            [{'publicKey' : 'A', 'quorumSet' : {'threshold' : 1, 'validators' : ['B'], 'innerQuorumSets' : []}},
             {'publicKey' : 'B', 'quorumSet' : {'threshold' : 1, 'validators' : ['A'], 'innerQuorumSets' : []}},
             {'publicKey' : 'C', 'quorumSet' : {'threshold' : 1, 'validators' : ['D'], 'innerQuorumSets' : []}},
             {'publicKey' : 'D', 'quorumSet' : {'threshold' : 1, 'validators' : ['C'], 'innerQuorumSets' : []}},
             {'publicKey' : 'E', 'quorumSet' : {'threshold' : 2,
                                                'validators' : [],
                                                'innerQuorumSets' : [
                                                    {'threshold' : 1, 'validators' : ['A','B'], 'innerQuorumSets' : []},
                                                    {'threshold' : 1, 'validators' : ['C','D'], 'innerQuorumSets' : []},
                                                ]}}])
        self.assertFalse(tvlc.check_network_intertwined(network))
        self.assertTrue(tvlc.check_intertwined(network,'A','B'))
        self.assertTrue(tvlc.check_intertwined(network,'A','E'))
        self.assertTrue(tvlc.check_intertwined(network,'D','E'))
        self.assertFalse(tvlc.check_intertwined(network,'A','C'))