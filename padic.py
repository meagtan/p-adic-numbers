from fractions import Fraction
from sys import maxint
from modp import *

def padic(prime):
    'Return p-adic class with given prime.'
    class Res(PAdic):
        p = prime
    return Res

class PAdic:
    p = 2 # default
    def __init__(self):
        self.val  = '' # current known value
        self.prec = 0 # current known precision
        self.order = 0 # order/valuation of number
        pass # initialize object as subclass perhaps
    
    def get(self, prec):
        'Return value of number with given precision.'
        if self.value == 0:
            return '0' # * prec
        
        while self.prec < prec:
            # update val based on value
            self._nextdigit()
            self.prec += 1
        return self.val # TODO add decimal point or trailing zeros
    
    def _nextdigit(self):
        'Calculate next digit of p-adic number.'
        raise NotImplementedError
    
    # return value with precision up to 32 bits
    def __int__(self):
        return int(self.get(32), p)
    def __str__(self):
        return self.get(32)
    def __repr__(self):
        pass
    
    # arithmetic operations
    def __add__(self, other):
        return PAdicAdd(self, other)
    def __radd__(self, other):
        return PAdicAdd(other, self)
    def __sub__(self, other):
        return PAdicAdd(self, PAdicInv(other))
    def __rsub__(self, other):
        return PAdicAdd(other, PAdicInv(self))
    def __smul__(self, other):
        return PAdicMul(self, other)
    def __rsub__(self, other):
        return PAdicMul(other, self)
    
    # p-adic norm
    def __abs__(self):
        if self.order == maxint:
            return 0
        norm = Fraction(1)
        if self.order > 0:
            norm.numerator = p ** self.order
        if self.order < 0:
            norm.denominator = p ** self.order
        return norm

class PAdicConst(PAdic):
    def __init__(self, value):
        PAdic.__init__(self)
        value = Fraction(value)
        
        # calculate valuation
        if value == 0:
            self.value = value
            self.val = '0'
            return
        
        self.norm = Fraction(1)
        self.order = 0
        while not value.numerator % p:
            self.norm /= p
            self.order += 1
            value.numerator /= p
        while not value.denominator % p:
            self.norm *= p
            valuation -= 1
            value.denominator /= p
        self.value = value
    
    def _nextdigit(self):
        'Calculate next digit of p-adic number.'
        rem = ModP(p, self.value.numerator) / ModP(p, self.value.denominator)
        self.val = rem + self.val
        self.value -= rem
        self.value /= p

     