from fractions import Fraction
from sys import maxint
from modp import *

class PAdic:
    def __init__(self, p):
        self.p = p
        self.val  = '' # current known value
        self.prec = 0 # current known precision, also containing leading zeros
        self.order = 0 # order/valuation of number
        pass # initialize object as subclass perhaps
    
    def get(self, prec):
        'Return value of number with given precision.'
        while self.prec < prec:
            # update val based on value
            self.val = self._nextdigit() + self.val
            self.prec += 1
        return self.val # TODO add decimal point or trailing zeros
    
    def _nextdigit(self):
        'Calculate next digit of p-adic number.'
        raise NotImplementedError
    
    def getdigit(self, index):
        'Return digit at given index.'
        return int(self.get(index+1)[0])
    
    # return value with precision up to 32 bits
    def __int__(self):
        return int(self.get(32), p)
    def __str__(self):
        return self.get(32)
    
    # arithmetic operations
    def __add__(self, other):
        return PAdicAdd(self.p, self, other)
    def __radd__(self, other):
        return PAdicAdd(self.p, other, self)
    def __sub__(self, other):
        return PAdicAdd(self.p, self, PAdicNeg(self.p, other))
    def __rsub__(self, other):
        return PAdicAdd(self.p, other, PAdicNeg(self.p, self))
    def __smul__(self, other):
        return PAdicMul(self.p, self, other)
    def __rsub__(self, other):
        return PAdicMul(self.p, other, self)
    
    # p-adic norm
    def __abs__(self):
        if self.order == maxint:
            return 0
        norm = Fraction(1)
        if self.order > 0:
            norm.numerator = self.p ** self.order
        if self.order < 0:
            norm.denominator = self.p ** self.order
        return norm

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
            self.prec += 1
            value.numerator /= self.p
        while not value.denominator % self.p:
            valuation -= 1
            value.denominator /= self.p
        self.value = value
    
    def get(self, prec):
        if self.value == 0:
            return '0' # * prec
        return PAdic.get(self, prec)
    
    def _nextdigit(self):
        'Calculate next digit of p-adic number.'
        rem = ModP(self.p, self.value.numerator) / ModP(self.p, self.value.denominator)
        self.value -= rem
        self.value /= self.p
        return rem

class PAdicAdd(PAdic):
    'Sum of two p-adic numbers.'
    def __init__(self, p, arg1, arg2):
        PAdic.__init__(self, p)
        self.carry = 0
        self.arg1 = arg1
        self.arg2 = arg2
        self.order = min(arg1.order, arg2.order) # might be larger than this
        # loop until first nonzero digit is found
        digit = self._nextdigit()
        while digit == 0:
            self.order += 1
            self.prec += 1
            digit = self._nextdigit()
    
    def _nextdigit(self):
        s = self.arg1.getdigit(self.prec) + self.arg2.getdigit(self.prec) + self.carry
        self.carry = s // self.p
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
        return self.p - 1 - self.arg.getdigit(0)

class PAdicMul(PAdic):
    'Product of two p-adic numbers.'
    def __init__(self, p, arg1, arg2):
        PAdic.__init__(self, p)
        self.carry = 0
        self.arg1 = arg1
        self.arg2 = arg2
    
    def _nextdigit(self):
        s = sum(self.arg1.getdigit(i) * self.arg2.getdigit(self.prec - i) for i in xrange(self.prec + 1)) + self.carry
        self.carry = s // self.p
        return s % self.p 