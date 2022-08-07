#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
#
#  License: GLP3+
#  Copyright 2017 meagtan
#  Copyright 2022 Beat Jäckle <beat@git.jdmweb2.ch>


from fractions import Fraction
from sys import maxsize
from modp import ModP


class PAdic:
    def __init__(self, p, printInvers=False):
        self.p = p

        # current known value
        self.digitP = []  # digitP[0]=c_0; digitP[i]=c_i
        self.digitN = []  # digitN[0]=c_-1; digitN[i]=c_-1-i
        self.prec = 0  # current known precision, not containing trailing zeros

        self.order = 0  # order/valuation of number
        self.printInvers = printInvers
        return None

    def calc(self, prec):
        # First calculation
        if len(self.digitN) + len(self.digitP) == 0:
            if self.value == 0:
                self.zero = True
                self.digitP = [0]
                return None
            if self.order < 0:
                absorder = abs(self.order)
                self.digitN = [None]*absorder
                for i in range(absorder):
                    self.digitN[absorder-i-1] = self._nextdigit()
                if absorder >= prec:
                    self.prec = absorder
                self.digitP.append(self._nextdigit())
            elif self.order > 0:
                self.digitP = [0]*self.order
        while len(self.digitN) + len(self.digitP) < prec:
            if self.value == 0:
                break
            self.digitP.append(self._nextdigit())
        return None

    def get(self, prec, decimal=True):
        self.calc(prec)
        'Return value of number with given precision.'
        s = ''
        for d in self.digitP[::-1]:
            s += str(d)
        if self.digitN:
            if decimal:
                s += '.'
            for d in self.digitN:
                s += str(d)
        return s

    def _nextdigit(self):
        'Calculate next digit of p-adic number.'
        raise NotImplementedError

    def getdigit(self, index):
        if index < self.order:
            # print('not relevant 0')
            return 0

        # be sure to calculate the digits
        prec = index+1
        if self.order < 0:
            prec += abs(self.order)
        self.calc(prec)

        # negative index
        if index < 0:
            try:
                return self.digitN[abs(index)-1]
            except IndexError:
                print('Should not happen', index)
                print('__dict__', self.__dict__())
                raise IndexError(
                    f"Digit not Found\n"
                    f"index: {index}\n"
                    f"dict: {self.__dict__()}"
                    )

        # positive index
        else:
            try:
                return self.digitP[index]
            except IndexError:
                if self.value == 0:
                    # print('not significant',0)
                    return 0
                else:
                    print('Logical Error')
                    print(f'Index = {index}')
                    print(f'pAdic = {self.__dict__()}')
                    raise ValueError('Logical Error')

    # return value with precision up to 32 bits
    def __int__(self):
        return int(self.get(32), self.p)

    def __getitem__(self, index):
        return self.getdigit(index)

    def __str__(self):
        if self.printInvers:
            return self.get(32)[::-1]
        return self.get(32)

    def __repr__(self):
        return str(self)

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
        if self.order == maxsize:
            return 0
        numer = denom = 1
        if self.order > 0:
            numer = self.p ** self.order
        if self.order < 0:
            denom = self.p ** self.order
        return Fraction(numer, denom)

    # determines the p-value of an p-adic number
    def pValue(self):
        return self.order

    def fractionvalue(self):
        self.calc(1)
        s = Fraction(0)
        for (i, d) in enumerate([self.digitP[0]]+self.digitN):
            s += Fraction(d, self.p**i)
        return s

    def getOffset(self):
        if self.order >= 0:
            return 0
        else:
            return -self.order


class PAdicConst(PAdic):
    def __init__(self, p, value, printInvers=False):
        super().__init__(p, printInvers)
        value = Fraction(value)

        # calculate valuation
        if value == 0:
            self.value = value
            self.order = float('inf')
            self.zero = True
            return None

        while not value.numerator % self.p:
            self.order += 1
            value /= self.p
        while not value.denominator % self.p:
            self.order -= 1
            value *= self.p
        self.value = value
        return None

    def get(self, prec, decimal=True):
        if self.zero:
            return '0' * prec
        return PAdic.get(self, prec, decimal)

    def _nextdigit(self):
        'Calculate next digit of p-adic number.'
        rem = int(
            ModP(self.p, self.value.numerator) *
            ModP(self.p, self.value.denominator)._inv()
            )
        self.value -= rem
        self.value /= self.p
        return rem


class PAdicAdd(PAdic):
    'Sum of two p-adic numbers.'
    def __init__(self, p, arg1, arg2, printInvers=False):
        super.__init__(self, p, printInvers)
        self.carry = 0
        _nextdigitCache = []
        self.arg1 = arg1
        self.arg2 = arg2
        # might be larger than this
        self.order = self.prec = min(arg1.order, arg2.order)
        arg1.order -= self.order
        arg2.order -= self.order
        # loop until first nonzero digit is found
        self.index = self.order
        digit = self._nextdigit()
        while digit == 0:
            self.index += 1
            digit = self._nextdigit()
        self.order = self.index
        _nextdigitCache.append(digit)

    def _nextdigit(self):
        if _nextdigitCache:
            return _nextdigitCache.pop()
        s = self.arg1.getdigit(self.index) + \
            self.arg2.getdigit(self.index) + self.carry
        self.carry = s // self.p
        self.index += 1
        return s % self.p


class PAdicNeg(PAdic):
    'Negation of a p-adic number.'
    def __init__(self, p, arg, printInvers=False):
        super.__init__(self, p, printInvers)
        self.arg = arg
        self.order = arg.order

    def _nextdigit(self):
        if self.prec == 0:
            # cannot be p, 0th digit of arg must be nonzero
            return self.p - self.arg.getdigit(0 - self.getOffset())
        return self.p - 1 - self.arg.getdigit(self.prec - self.getOffset())


class PAdicMul(PAdic):
    'Product of two p-adic numbers.'
    def __init__(self, p, arg1, arg2):
        PAdic.__init__(self, p)
        self.carry = 0
        self.arg1 = arg1
        self.arg2 = arg2
        self.order = arg1.order + arg2.order
        self.arg1.order = self.arg2.order = 0  # TODO requires copy
        self.index = 0

    def _nextdigit(self):
        s = sum(
            self.arg1.getdigit(i) * self.arg2.getdigit(self.index - i)
            for i in xrange(self.index + 1)
            ) + self.carry
        self.carry = s // self.p
        self.index += 1
        return s % self.p
