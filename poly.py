# Polynomial class on Z or Z_p

from collections import defaultdict

class Poly:
    'Polynomial class.'
    def __init__(self, coeffs = None):
        self.coeffs = defaultdict(int, not coeffs and {} or isinstance(coeffs, int) and {0:coeffs} or coeffs)
        self.deg = int(self.coeffs and max(self.coeffs.keys()))
    
    # arithmetic
    def __add__(self, other):
        if not isinstance(other, Poly):
            other = Poly(other)
        res = Poly()
        res.deg = max(self.deg, other.deg)
        for i in xrange(res.deg+1):
            res.coeffs[i] = self.coeffs[i] + other.coeffs[i]
        return res
    def __radd__(self, other):
        if not isinstance(other, Poly):
            other = Poly(other)
        return other.__add__(self)
    def __sub__(self, other):
        if not isinstance(other, Poly):
            other = Poly(other)
        return self.__add__(other._neg())
    def __rsub__(self, other):
        if not isinstance(other, Poly):
            other = Poly(other)
        return other.__add__(self._neg())
    
    def __mul__(self, other):
        if not isinstance(other, Poly):
            other = Poly(other)
        res = Poly()
        res.deg = self.deg + other.deg
        for i in xrange(res.deg+1):
            for j in xrange(i+1):
                res.coeffs[i] += self.coeffs[j] * other.coeffs[i - j]
        return res
    def __rmul__(self, other):
        if not isinstance(other, Poly):
            other = Poly(other)
        return other.__mul__(self)

X = Poly({1:1})