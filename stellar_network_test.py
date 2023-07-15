import stellar_network
import unittest

class QSetTest(unittest.TestCase):
    def test_1(self):
        qset = stellar_network.QSet.from_json(
            {'threshold' : 1, 'validators' : ['A'], 'innerQuorumSets' : []})
    def test_2(self):
        qset = stellar_network.QSet.from_json(
            {'threshold' : 1, 'validators' : ['A'], 'innerQuorumSets' :
                [{'threshold' : 1, 'validators' : ['B'], 'innerQuorumSets' : []},
                 {'threshold' : 1, 'validators' : ['C','D'], 'innerQuorumSets' : []}]})

class TestStellarNetwork(unittest.TestCase):
    def test_1(self):
        network = stellar_network.StellarNetwork(
            [{'publicKey' : 'A', 'quorumSet' : {'threshold' : 1, 'validators' : ['A'], 'innerQuorumSets' : []}}])
        self.assertTrue(network.check_network_intertwined())

    def test_2(self):
        network = stellar_network.StellarNetwork(
            [{'publicKey' : 'A', 'quorumSet' : {'threshold' : 1, 'validators' : ['B'], 'innerQuorumSets' : []}},
             {'publicKey' : 'B', 'quorumSet' : {'threshold' : 1, 'validators' : ['A'], 'innerQuorumSets' : []}}])
        formula = network.network_intertwined()
        # write the formula to the file log.txt:
        with open('log.txt', 'w') as f:
            f.write(formula.serialize())
        self.assertTrue(network.check_network_intertwined())

    def test_3(self):
        network = stellar_network.StellarNetwork(
            [{'publicKey' : 'A', 'quorumSet' : {'threshold' : 1, 'validators' : ['B'], 'innerQuorumSets' : []}},
             {'publicKey' : 'B', 'quorumSet' : {'threshold' : 1, 'validators' : ['B'], 'innerQuorumSets' : []}}])
        self.assertTrue(network.check_network_intertwined())

    def test_4(self):
        network = stellar_network.StellarNetwork(
            [{'publicKey' : 'A', 'quorumSet' : {'threshold' : 1, 'validators' : ['A'], 'innerQuorumSets' : []}},
             {'publicKey' : 'B', 'quorumSet' : {'threshold' : 1, 'validators' : ['B'], 'innerQuorumSets' : []}}])
        self.assertFalse(network.check_network_intertwined())

    def test_5(self):
        network = stellar_network.StellarNetwork(
            [{'publicKey' : 'A', 'quorumSet' : {'threshold' : 1, 'validators' : ['B'], 'innerQuorumSets' : []}},
             {'publicKey' : 'B', 'quorumSet' : {'threshold' : 1, 'validators' : ['C'], 'innerQuorumSets' : []}},
             {'publicKey' : 'C', 'quorumSet' : {'threshold' : 1, 'validators' : ['A'], 'innerQuorumSets' : []}}])
        self.assertTrue(network.check_network_intertwined())

    def test_6(self):
        network = stellar_network.StellarNetwork(
            [{'publicKey' : 'A', 'quorumSet' : {'threshold' : 1, 'validators' : ['B'], 'innerQuorumSets' : []}},
             {'publicKey' : 'B', 'quorumSet' : {'threshold' : 1, 'validators' : ['A'], 'innerQuorumSets' : []}},
             {'publicKey' : 'C', 'quorumSet' : {'threshold' : 1, 'validators' : ['B','D'], 'innerQuorumSets' : []}},
             {'publicKey' : 'D', 'quorumSet' : {'threshold' : 1, 'validators' : ['A','D'], 'innerQuorumSets' : []}}])
        self.assertFalse(network.check_network_intertwined())
        self.assertTrue(network.check_intertwined('A','B'))
        self.assertFalse(network.check_intertwined('A','C'))

    def test_7(self):
        network = stellar_network.StellarNetwork(
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
        self.assertFalse(network.check_network_intertwined())
        self.assertTrue(network.check_intertwined('A','B'))
        self.assertTrue(network.check_intertwined('A','E'))
        self.assertTrue(network.check_intertwined('D','E'))
        self.assertFalse(network.check_intertwined('A','C'))