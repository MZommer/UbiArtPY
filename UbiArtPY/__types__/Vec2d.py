import math
from .__base__ import float32

def isNaN(num: float32):
    return num != num

class Vec2d:
    X: float32 = 0.
    Y: float32 = 0.

    def __str__(self):
        return f"x: {self.X}, y: {self.Y}"

    def Min(self, _v):
        self.X = min(self.X, _v.X)
        self.Y = min(self.Y, _v.Y)

    def Max(self, _v):
        self.X = max(self.X, _v.X)
        self.Y = max(self.Y, _v.Y)
    
    def setNull(self):
        self.X = self.Y = 0.
    
    def isNull(self):
        return self.X and self.Y
    
    def isNaN(self):
        return isNaN(self.X) or isNaN(self.Y)
    
    # Operators
    def __mul__(self, _s):
        return Vec2d(self.X * _s, self.Y * _s)
    
    def __imul__(self, _s):
        self.X *= _s
        self.Y *= _s
    
    def __div__(self, _s):
        return Vec2d(self.X / _s, self.Y / _s)
    
    def __idiv__(self, _s):
        self.X /= _s
        self.Y /= _s
    
    def __sum__(self, _s):
        if isinstance(_s, Vec2d):
            return Vec2d(self.X + _s.X, self.Y + _s.Y)
        return Vec2d(self.X + _s, self.Y + _s)
    
    def __isum__(self, _s):
        if isinstance(_s, Vec2d):
            self.X += _s.X
            self.Y += _s.Y
        else:
            self.X += _s
            self.Y += _s

    def __sub__(self, _s):
        if isinstance(_s, Vec2d):
            return Vec2d(self.X - _s.X, self.Y - _s.Y)
        return Vec2d(self.X - _s, self.Y - _s)
    
    def __isub__(self, _s):
        if isinstance(_s, Vec2d):
            self.X -= _s.X
            self.Y -= _s.Y
        self.X -= _s
        self.Y -= _s
    
    def __eq__(self, _s) -> bool:
        return math.isclose(self.X, _s) and math.isclose(self.Y, _s.Y)

    def __ne__(self, _s) -> bool:
        return not (self == _s)