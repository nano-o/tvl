"""
This files contains a prototype implementation of validity checking of a 3-valued, paraconsistent logic by reduction to SAT.
It is based on code written by Yoni Zohar (yoni.zohar@cs.tau.ac.il)
"""

from pysmt.walkers import IdentityDagWalker
import pysmt.shortcuts as ps

AND = ps.Symbol("and", ps.FunctionType(ps.BOOL, [ps.BOOL, ps.BOOL]))
OR = ps.Symbol("or", ps.FunctionType(ps.BOOL, [ps.BOOL, ps.BOOL]))
NOT = ps.Symbol("not", ps.FunctionType(ps.BOOL, [ps.BOOL]))
# NOTE diamond or box have to be primitives as (I think) there's no way to express them in terms of and, or, and not
DIAMOND = ps.Symbol("diamond", ps.FunctionType(ps.BOOL, [ps.BOOL]))

# The constant F
F = ps.Symbol("F", ps.BOOL)

def And(x,y):
  return ps.Function(AND, [x, y])

def Or(x,y):
  return ps.Function(OR, [x, y])

def Not(x):
  return ps.Function(NOT, [x])

# C for curly
def Cimp(x,y):
    return Or(Not(x), y)

def Ciff(x,y):
    return And(Cimp(x,y), Cimp(y,x))

# D for Double
def Dimp(x,y):
    return Cimp(Diamond(x), y)

def Diff(x,y):
    return And(Dimp(x,y), Dimp(y,x))

def Box(x):
    return Dimp(Not(x), F)

def Diamond(x):
    return ps.Function(DIAMOND, [x])

def B(x):
    return Diamond(x, Not(x))

class ExtendedIdentityDagWalker(IdentityDagWalker):
    def __init__(self):
        IdentityDagWalker.__init__(self)
        self.subformulas_to_bools_TB = {}
        self.subformulas_to_bools_FB = {}
        self.constraints = set({})

    def is_T(self, x):
        x_is_TB = self.subformulas_to_bools_TB[x]
        x_is_FB = self.subformulas_to_bools_FB[x]
        return ps.And(x_is_TB, ps.Not(x_is_FB))
    
    def is_B(self, x):
        x_is_TB = self.subformulas_to_bools_TB[x]
        x_is_FB = self.subformulas_to_bools_FB[x]
        return ps.And(x_is_TB, x_is_FB)
    
    def is_F(self, x):
        x_is_TB = self.subformulas_to_bools_TB[x]
        x_is_FB = self.subformulas_to_bools_FB[x]
        return ps.And(ps.Not(x_is_TB), x_is_FB)
    
    def add_to_caches(self, formula):
        if formula not in self.subformulas_to_bools_TB:
            assert formula not in self.subformulas_to_bools_FB
            self.subformulas_to_bools_TB[formula] = ps.Symbol("is_TB(" + str(formula) + ")")
            self.subformulas_to_bools_FB[formula] = ps.Symbol("is_FB(" + str(formula) + ")")
        assert formula in self.subformulas_to_bools_FB
        self.constraints.add(ps.Or(self.subformulas_to_bools_TB[formula], self.subformulas_to_bools_FB[formula]))

    def walk_symbol(self, formula, *args, **kwargs):
        self.add_to_caches(formula)
        if formula == F:
            f_is_TB = self.subformulas_to_bools_TB[formula]
            f_is_FB = self.subformulas_to_bools_FB[formula]
            constraint = ps.And(ps.Not(f_is_TB), f_is_FB)
            self.constraints.add(constraint)

    def walk_function(self, formula, *args, **kwargs):
        self.add_to_caches(formula)
        connective = formula.function_name()
        if connective == AND:
            assert(len(formula.args()) == 2)
            left = formula.args()[0]
            right = formula.args()[1]
            cell11 = ps.Implies(ps.And(self.is_T(left), self.is_T(right)), self.is_T(formula))
            cell12 = ps.Implies(ps.And(self.is_T(left), self.is_B(right)), self.is_B(formula))
            cell13 = ps.Implies(ps.And(self.is_T(left), self.is_F(right)), self.is_F(formula))
            cell21 = ps.Implies(ps.And(self.is_B(left), self.is_T(right)), self.is_B(formula))
            cell22 = ps.Implies(ps.And(self.is_B(left), self.is_B(right)), self.is_B(formula))
            cell23 = ps.Implies(ps.And(self.is_B(left), self.is_F(right)), self.is_F(formula))
            cell31 = ps.Implies(ps.And(self.is_F(left), self.is_T(right)), self.is_F(formula))
            cell32 = ps.Implies(ps.And(self.is_F(left), self.is_B(right)), self.is_F(formula))
            cell33 = ps.Implies(ps.And(self.is_F(left), self.is_F(right)), self.is_F(formula))
            self.constraints.add(ps.And(cell11, cell12, cell13, cell21, cell22, cell23, cell31, cell32, cell33))
        elif connective == OR:
            assert(len(formula.args()) == 2)
            left = formula.args()[0]
            right = formula.args()[1]
            cell11 = ps.Implies(ps.And(self.is_T(left), self.is_T(right)), self.is_T(formula))
            cell12 = ps.Implies(ps.And(self.is_T(left), self.is_B(right)), self.is_T(formula))
            cell13 = ps.Implies(ps.And(self.is_T(left), self.is_F(right)), self.is_T(formula))
            cell21 = ps.Implies(ps.And(self.is_B(left), self.is_T(right)), self.is_T(formula))
            cell22 = ps.Implies(ps.And(self.is_B(left), self.is_B(right)), self.is_B(formula))
            cell23 = ps.Implies(ps.And(self.is_B(left), self.is_F(right)), self.is_B(formula))
            cell31 = ps.Implies(ps.And(self.is_F(left), self.is_T(right)), self.is_T(formula))
            cell32 = ps.Implies(ps.And(self.is_F(left), self.is_B(right)), self.is_B(formula))
            cell33 = ps.Implies(ps.And(self.is_F(left), self.is_F(right)), self.is_F(formula))
            self.constraints.add(ps.And(cell11, cell12, cell13, cell21, cell22, cell23, cell31, cell32, cell33))
        elif connective == NOT:
            assert(len(formula.args()) == 1)
            child = formula.args()[0]
            cell1 = ps.Implies(self.is_T(child), self.is_F(formula))
            cell2 = ps.Implies(self.is_B(child), self.is_B(formula))
            cell3 = ps.Implies(self.is_F(child), self.is_T(formula))
            self.constraints.add(ps.And(cell1, cell2, cell3))
        elif connective == DIAMOND:
            assert(len(formula.args()) == 1)
            child = formula.args()[0]
            cell1 = ps.Implies(self.is_T(child), self.is_T(formula))
            cell2 = ps.Implies(self.is_B(child), self.is_T(formula))
            cell3 = ps.Implies(self.is_F(child), self.is_F(formula))
            self.constraints.add(ps.And(cell1, cell2, cell3))

def encode_tables(formula):
    walker = ExtendedIdentityDagWalker()
    walker.walk(formula)
    return walker.constraints, walker.subformulas_to_bools_TB, walker.subformulas_to_bools_FB

def translate_for_validity(formula):
    """
    Translate a formula in three-valued logic to a formula in classical logic that is valid iff the original formula is valid.
    """
    constraints, subformulas_to_bools_TB, _ = encode_tables(formula)
    return ps.Implies(ps.And([c for c in constraints]), subformulas_to_bools_TB[formula])

def is_valid(formula):
    return ps.is_valid(translate_for_validity(formula))

def translate_for_satisfiability(formula):
    """
    Translate a formula in three-valued logic to a formula in classical logic that is satisfiable iff the original formula is satisfiable.
    """
    constraints, subformulas_to_bools_TB, _ = encode_tables(formula)
    return ps.And([c for c in constraints] + [subformulas_to_bools_TB[formula]])

def is_sat(formula):
    return ps.is_sat(translate_for_satisfiability(formula))