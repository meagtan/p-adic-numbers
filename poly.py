# Finding roots of polynomials in p-adic integers using Hensel's lemma

from padic import *
from collections import defaultdict

class Poly:
    'Polynomial class.'
    def __init__(self, coeffs = None):
        self.coeffs = defaultdict(int, coeffs or {})
        self.deg = 0
    # TODO arithmetic

X = Poly({1:1})

class ConstPoly(Poly):
    'Constant polynomial.'
    def __init__(self, coeff):
        Poly.__init__(self, {0:coeff})
