# Finding roots of polynomials in p-adic integers using Hensel's lemma

from padic import *
from poly import *

class PAdicPoly(PAdic):
    'Result of lifting a root of a polynomial in the integers mod p to the p-adic integers.'
    def __init__(self, p, poly, root):
        PAdic.__init__(self, p)
        self.root = root
        self.poly = poly
        self.deriv = derivative(poly)
        
        # argument checks for the algorithm to work
        if poly(root) % p:
            raise ValueError("%d is not a root of %s modulo %d" % (root, poly, p))
        if self.deriv(root) % p == 0:
            raise ValueError("Polynomial %s is not separable modulo %d" % (poly, p))
        
        # take care of trailing zeros
        digit = self.root
        self.val = str(digit)
        self.exp = self.p
        while digit == 0:
            self.order += 1
            digit = self._nextdigit()
            # self.prec += 1

    def _nextdigit(self):
        self.root = ModP(self.exp * self.p, self.root)
        self.root = self.root - self.poly(self.root) / self.deriv(self.root) # coercions automatically taken care of
        digit = self.root // self.exp
        self.exp *= self.p
        return digit