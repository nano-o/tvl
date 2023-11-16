import unittest
import stellar_network as sn

class QSetTest(unittest.TestCase):
    def test_1(self):
        qset = sn.QSet.from_json(
            {'threshold' : 1, 'validators' : ['A'], 'innerQuorumSets' : []})
    def test_2(self):
        qset = sn.QSet.from_json(
            {'threshold' : 1, 'validators' : ['A'], 'innerQuorumSets' :
                [{'threshold' : 1, 'validators' : ['B'], 'innerQuorumSets' : []},
                 {'threshold' : 1, 'validators' : ['C','D'], 'innerQuorumSets' : []}]})
        
class SymmetricNetworkTest(unittest.TestCase):
    def test_1(self):
        network = sn.StellarNetwork.symmetric_network(3)
        self.assertTrue(len(network.validators) == 3*3)
        self.assertTrue(network.validators['org0v0'].threshold == 3)
        self.assertTrue(network.validators['org0v0'].validators == frozenset())
        self.assertTrue(network.validators['org0v0'].innerQuorumSets == frozenset({sn.QSet(threshold=2, validators=frozenset({'org2v2', 'org2v1', 'org2v0'}), innerQuorumSets=frozenset()), sn.QSet(threshold=2, validators=frozenset({'org1v2', 'org1v1', 'org1v0'}), innerQuorumSets=frozenset()), sn.QSet(threshold=2, validators=frozenset({'org0v2', 'org0v0', 'org0v1'}), innerQuorumSets=frozenset())}))
        
class BlockingTest(unittest.TestCase):
    def test_1(self):
        qset = sn.QSet.from_json(
            {'threshold' : 1, 'validators' : ['AB'], 'innerQuorumSets' : []})
        self.assertTrue(sn.blocking(qset) == frozenset([frozenset(['AB'])]))

    def test_2(self):
        qset = sn.QSet.from_json(
            {'threshold' : 2, 'validators' : ['A','B','C'], 'innerQuorumSets' : []})
        self.assertTrue(sn.blocking(qset) == frozenset({frozenset({'B', 'C'}), frozenset({'B', 'A'}), frozenset({'A', 'C'})}))

    def test_3(self):
        qset = sn.QSet.from_json(
            {'threshold' : 3, 'validators' : ['A','B','C'], 'innerQuorumSets' :
             [{'threshold' : 2, 'validators' : ['1','2','3'], 'innerQuorumSets' : []}]})
        res = frozenset({frozenset({'C', '2', '1'}), frozenset({'B', '2', '3'}), frozenset({'A', '3', '1'}), frozenset({'A', 'C'}), frozenset({'A', 'B'}), frozenset(
            {'B', '2', '1'}), frozenset({'C', '3', '1'}), frozenset({'B', '3', '1'}), frozenset({'A', '2', '1'}), frozenset({'B', 'C'}), frozenset({'A', '2', '3'}), frozenset({'2', '3', 'C'})})
        self.assertTrue(sn.blocking(qset) == res)

    def test_4(self):
        qset = sn.QSet.from_json(
            {'threshold' : 1, 'validators' : [], 'innerQuorumSets' : 
             [{'threshold' : 2, 'validators' : ['1','2','3'], 'innerQuorumSets' : []},
              {'threshold' : 2, 'validators' : ['A','B','C'], 'innerQuorumSets' : []}]})
        res = frozenset({frozenset({'A', '2', '3', 'C'}), frozenset({'A', 'C', '1', '3'}), frozenset({'A', 'B', '1', '3'}), frozenset({'A', '2', 'B', '1'}), frozenset({'A', '2', 'B', '3'}), frozenset({'A', '2', '1', 'C'}), frozenset({'3', 'B', '1', 'C'}), frozenset({'2', 'B', '3', 'C'}), frozenset({'2', 'B', '1', 'C'})})
        self.assertTrue(sn.blocking(qset) == res)
