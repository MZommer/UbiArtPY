import math
from .__base__ import float32

def isNaN(num: float32):
    return num != num

class Vec3d:
    X: float32 = 0.
    Y: float32 = 0.
    Z: float32 = 0.

    def __init__(self, _x: float32, _y: float32, _z: float32) -> None:
        self.X = float32(_x)
        self.Y = float32(_y)
        self.Z = float32(_z)

    def __str__(self):
        return f"x: {self.X}, y: {self.Y}, z: {self.Z}"

    def Min(self, _v):
        self.X = min(self.X, _v.X)
        self.Y = min(self.Y, _v.Y)
        self.Z = min(self.Z, _v.Z)

    def Max(self, _v):
        self.X = max(self.X, _v.X)
        self.Y = max(self.Y, _v.Y)
        self.Z = max(self.Z, _v.Z)
    
    def setNull(self):
        self.X = self.Y = self.Z = 0.
    
    def isNull(self):
        return self.X and self.Y and self.Z
    
    def isNaN(self):
        return isNaN(self.X) or isNaN(self.Y) or isNaN(self.Z)
    
    # Operators
    def __mul__(self, _s):
        return Vec3d(self.X * _s, self.Y * _s, self.Z * _s)
    
    def __imul__(self, _s):
        self.X *= _s
        self.Y *= _s
        self.Z *= _s
    
    def __div__(self, _s):
        return Vec3d(self.X / _s, self.Y / _s, self.Z / _s)
    
    def __idiv__(self, _s):
        self.X /= _s
        self.Y /= _s
        self.Z /= _s
    
    def __sum__(self, _s):
        if isinstance(_s, Vec3d):
            return Vec3d(self.X + _s.X, self.Y + _s.Y, self.Z + _s.Z)
        return Vec3d(self.X + _s, self.Y + _s, self.Z + _s)
    
    def __isum__(self, _s):
        if isinstance(_s, Vec3d):
            self.X += _s.X
            self.Y += _s.Y
            self.Z += _s.Z
        else:
            self.X += _s
            self.Y += _s
            self.Z += _s

    def __sub__(self, _s):
        if isinstance(_s, Vec3d):
            return Vec3d(self.X - _s.X, self.Y - _s.Y, self.Z - _s.Z)
        return Vec3d(self.X - _s, self.Y - _s, self.Z - _s)
    
    def __isub__(self, _s):
        if isinstance(_s, Vec3d):
            self.X -= _s.X
            self.Y -= _s.Y
            self.Z -= _s.Z
        self.X -= _s
        self.Y -= _s
        self.Z -= _s
    
    def __eq__(self, _s) -> bool:
        return math.isclose(self.X, _s) and math.isclose(self.Y, _s.Y) and math.isclose(self.Z, _s.Z)

    def __ne__(self, _s) -> bool:
        return not (self == _s)