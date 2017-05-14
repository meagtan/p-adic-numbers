class ModP(int):
    'Integers mod p, p a prime power.'
    def __new__(cls, p, num):
        self = int.__new__(cls, int(num) % p)
        self.p = p
        return self
    
    def __str__(self):
        return "%d (mod %d)" % (self, self.p)
    def __repr__(self):
        return "%d %% %d" % (self, self.p)
    
    # arithmetic
    def __add__(self, other):
        return ModP(self.p, int(self) + int(other))
    def __radd__(self, other):
        return ModP(self.p, int(other) + int(self))
    def __sub__(self, other):
        return ModP(self.p, int(self) - int(other))
    def __rsub__(self, other):
        return ModP(self.p, int(other) - int(self))
    def __mul__(self, other):
        return ModP(self.p, int(self) * int(other))
    def __rmul__(self, other):
        return ModP(self.p, int(other) * int(self))
    def __div__(self, other):
        if not isinstance(other, ModP):
            other = ModP(self.p, other)
        return self * other._inv()
    def __rdiv__(self, other):
        return other * self._inv()
    
    def _inv(self):
        'Find multiplicative inverse of self in Z mod p.'
        # extended Euclidean algorithm
        rcurr = self.p
        rnext = int(self)
        tcurr = 0
        tnext = 1
        
        while rnext:
            q = rcurr // rnext
            rcurr, rnext = rnext, rcurr - q * rnext
            tcurr, tnext = tnext, tcurr - q * tnext
        
        if rcurr != 1:
            raise ValueError("%d not a unit modulo %d" % (self, self.p))
        return ModP(self.p, tcurr)