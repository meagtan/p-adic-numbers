class ModP(int):
    'Integers mod p, p a prime power.'
    def __new__(cls, p, num):
        self.p = p
        return int.__new__(cls, num % p)
    
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
        return self * other._inv()
    def __rdiv__(self, other):
        return other * self._inv()
    
    def _inv(self):
        'Find multiplicative inverse of self in Z mod p.'
        pass