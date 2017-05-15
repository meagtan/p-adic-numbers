from fractions import Fraction
from sys import maxint
from modp import *

class PAdic:
    def __init__(self, p):
        self.p = p
        self.val  = '' # current known value
        self.prec = 0 # current known precision, not containing trailing zeros
        self.order = 0 # order/valuation of number
        pass # initialize object as subclass perhaps
    
    def get(self, prec, decimal = True):
        'Return value of number with given precision.'
        while self.prec < prec:
            # update val based on value
            self.val = str(int(self._nextdigit())) + self.val
            self.prec += 1
        if self.order < 0:
            return (self.val[:self.order] + ('.' if decimal else '') + self.val[self.order:])[-prec-1:]
        return (self.val + self.order * '0')[-prec:]
    
    def _nextdigit(self):
        'Calculate next digit of p-adic number.'
        raise NotImplementedError
    
    def getdigit(self, index):
        'Return digit at given index.'
        return int(self.get(index + 1, False)[0]) #int(self.get(index+1+int(index < -self.order))[-int(index < -self.order)])
    
    # return value with precision up to 32 bits
    def __int__(self):
        return int(self.get(32), self.p)
    def __str__(self):
        return self.get(32)
    
    # arithmetic operations
    def __neg__(self):
        return PAdicNeg(self.p, self)
    def __add__(self, other):
        return PAdicAdd(self.p, self, other)
    def __radd__(self, other):
        return PAdicAdd(self.p, other, self)
    def __sub__(self, other):
        return PAdicAdd(self.p, self, PAdicNeg(self.p, other))
    def __rsub__(self, other):
        return PAdicAdd(self.p, other, PAdicNeg(self.p, self))
    def __mul__(self, other):
        return PAdicMul(self.p, self, other)
    def __rmul__(self, other):
        return PAdicMul(self.p, other, self)
    
    # p-adic norm
    def __abs__(self):
        if self.order == maxint:
            return 0
        numer = denom = 1
        if self.order > 0:
            numer = self.p ** self.order
        if self.order < 0:
            denom = self.p ** self.order
        return Fraction(numer, denom)

class PAdicConst(PAdic):
    def __init__(self, p, value):
        PAdic.__init__(self, p)
        value = Fraction(value)
        
        # calculate valuation
        if value == 0:
            self.value = value
            self.val = '0'
            self.order = maxint
            return
        
        self.order = 0
        while not value.numerator % self.p:
            self.order += 1
            value /= self.p
        while not value.denominator % self.p:
            self.order -= 1
            value *= self.p
        self.value = value
        
        self.zero = not value
    
    def get(self, prec, decimal = True):
        if self.zero:
            return '0' * prec
        return PAdic.get(self, prec, decimal)
    
    def _nextdigit(self):
        'Calculate next digit of p-adic number.'
        rem = ModP(self.p, self.value.numerator) / ModP(self.p, self.value.denominator)
        self.value -= int(rem)
        self.value /= self.p
        return rem

class PAdicAdd(PAdic):
    'Sum of two p-adic numbers.'
    def __init__(self, p, arg1, arg2):
        PAdic.__init__(self, p)
        self.carry = 0
        self.arg1 = arg1
        self.arg2 = arg2
        self.order = self.prec = min(arg1.order, arg2.order) # might be larger than this
        arg1.order -= self.order
        arg2.order -= self.order
        # loop until first nonzero digit is found
        self.index = 0
        digit = self._nextdigit()
        while digit == 0:
            self.index += 1
            self.order += 1
            digit = self._nextdigit()
        self.val += str(int(digit))
        self.prec = 1
    
    def _nextdigit(self):
        s = self.arg1.getdigit(self.index) + self.arg2.getdigit(self.index) + self.carry
        self.carry = s // self.p
        self.index += 1
        return s % self.p 

class PAdicNeg(PAdic):
    'Negation of a p-adic number.'
    def __init__(self, p, arg):
        PAdic.__init__(self, p)
        self.arg = arg
        self.order = arg.order
    
    def _nextdigit(self):
        if self.prec == 0:
            return self.p - self.arg.getdigit(0) # cannot be p, 0th digit of arg must be nonzero
        return self.p - 1 - self.arg.getdigit(self.prec)

class PAdicMul(PAdic):
    'Product of two p-adic numbers.'
    def __init__(self, p, arg1, arg2):
        PAdic.__init__(self, p)
        self.carry = 0
        self.arg1 = arg1
        self.arg2 = arg2
        self.order = arg1.order + arg2.order
        self.arg1.order = self.arg2.order = 0 # TODO requires copy
        self.index = 0
    
    def _nextdigit(self):
        s = sum(self.arg1.getdigit(i) * self.arg2.getdigit(self.index - i) for i in xrange(self.index + 1)) + self.carry
        self.carry = s // self.p
        self.index += 1
        return s % self.p 