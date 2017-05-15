# Polynomial class on Z or Z_p

from collections import defaultdict

class Poly:
    'Polynomial class.'
    def __init__(self, coeffs = None):
        self.coeffs = defaultdict(int, isinstance(coeffs, int) and {0:coeffs} or coeffs or {})
        self.deg = int(len(self.coeffs) and max(self.coeffs.keys()))
    
    def __call__(self, val):
        'Evaluate polynomial for a given value.'
        res = 0
        for i in xrange(self.deg, -1, -1):
            res = res * val + self.coeffs[i]
        return res
    
    def __str__(self):
        def term(coeff, expt):
            if coeff == 1 and expt == 0:
                return '1'
            return ' * '.join(([] if coeff == 1 else [str(coeff)]) + ([] if expt == 0 else ['X'] if expt == 1 else ['X ** ' + expt]))
            
        return ' + '.join(term(self.coeffs[i], i) for i in self.coeffs if self.coeffs[i] != 0)
    def __repr__(self):
        return str(self)
    
    # arithmetic
    def __neg__(self):
        return Poly({(i, -self.coeffs[i]) for i in self.coeffs})
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
        return self.__add__(other.__neg__())
    def __rsub__(self, other):
        if not isinstance(other, Poly):
            other = Poly(other)
        return other.__add__(self.__neg__())
    
    def __mul__(self, other):
        if not isinstance(other, Poly):
            other = Poly(other)
        res = Poly()
        res.deg = self.deg + other.deg # consider case where other is 0
        for i in xrange(res.deg+1):
            for j in xrange(i+1):
                res.coeffs[i] += self.coeffs[j] * other.coeffs[i - j]
        return res
    def __rmul__(self, other):
        if not isinstance(other, Poly):
            other = Poly(other)
        return other.__mul__(self)
        
    def __pow__(self, other):
        if not isinstance(other, int) or other < 0:
            raise ValueError("Exponent %d is not a natural number" % other)
        res = Poly(1)
        while other:
            res *= self
            other -= 1
        return res

X = Poly({1:1})

def derivative(p):
    'Return derivative of polynomial.'
    return Poly({(i - 1, i * p.coeffs[i]) for i in p.coeffs if i != 0})