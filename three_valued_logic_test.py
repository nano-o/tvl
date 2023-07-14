import pysmt as ps
from three_valued_logic import *
import unittest

class TestThreeValuedLogic(unittest.TestCase):
    def test_1(self):
        self.assertTrue(is_valid(Not(F)))
    def test_2(self):
        """
        Let's say that p and q each have a unique witness that consists of the other.
        Then, ClosedAx will be (q => p) /\ (~q => ~p) /\ (p => q) /\ (~p => ~q).
        To check whether p and q are intertwined, we need to check whether {p,q} |= ClosedAx => ((p /\ q) \/ (~p /\ ~q))
        """
        p = ps.Symbol("p")
        q = ps.Symbol("q")
        ClosedAx = And(Dimp(q,p), And(Dimp(Not(q),Not(p)), And(Dimp(p,q), Dimp(Not(p),Not(q)))))
        formula = Dimp(ClosedAx, Or(And(p,q),And(Not(p),Not(q))))
        self.assertTrue(is_valid(formula))
    def test_3(self):
        """
        Now p and q each have a single witness that consists of r, so p and q are intertwined.
        """
        p = ps.Symbol("p")
        q = ps.Symbol("q")
        r = ps.Symbol("r")
        ClosedAx2 = And(Dimp(r,p), And(Dimp(Not(r),Not(p)), And(Dimp(p,q), Dimp(Not(p),Not(q)))))
        formula = Dimp(ClosedAx2, Or(And(p,q),And(Not(p),Not(q))))
        self.assertTrue(is_valid(formula))
    def test_4(self):
        """
        Now p's witness set is {{r}} and q's witness set is {{s}}. So p and q are not intertwined.
        """
        p = ps.Symbol("p")
        q = ps.Symbol("q")
        r = ps.Symbol("r")
        s = ps.Symbol("s")
        ClosedAx3 = And(Dimp(r,p), And(Dimp(Not(r),Not(p)), And(Dimp(s,q), Dimp(Not(s),Not(q)))))
        formula = Dimp(ClosedAx3, Or(And(p,q),And(Not(p),Not(q))))
        self.assertFalse(is_valid(formula))