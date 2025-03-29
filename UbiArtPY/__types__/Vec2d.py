import math
from typing import Union, SupportsFloat

import numpy

from .__base__ import float32
from ..Core.SerializableClass import serializable_class


@serializable_class
class Vec2d:
    x: float32
    y: float32

    def __init__(self, x: SupportsFloat = 0, y: SupportsFloat = 0) -> None:
        self.x = float32(x)
        self.y = float32(y)

    def __str__(self) -> str:
        return f"x: {self.x}, y: {self.y}"

    def __repr__(self) -> str:
        return f"Vec2d(x={self.x}, y={self.y})"

    def min(self, other: 'Vec2d') -> None:
        if not isinstance(other, Vec2d):
            raise TypeError("Argument must be a Vec2d")
        self.x = numpy.min(self.x, other.x)
        self.y = numpy.min(self.y, other.y)

    def max(self, other: 'Vec2d') -> None:
        if not isinstance(other, Vec2d):
            raise TypeError("Argument must be a Vec2d")
        self.x = numpy.max(self.x, other.x)
        self.y = numpy.max(self.y, other.y)

    def set_null(self) -> None:
        self.x = self.y = float32()

    def is_null(self) -> bool:
        return self.x == 0 and self.y == 0

    def is_nan(self) -> bool:
        return math.isnan(self.x) or math.isnan(self.y)

    # Operators
    def __mul__(self, other: Union[SupportsFloat, 'Vec2d']) -> 'Vec2d':
        if isinstance(other, Vec2d):
            return Vec2d(self.x * other.x, self.y * other.y)
        return Vec2d(self.x * other, self.y * other)

    def __imul__(self, other: Union[SupportsFloat, 'Vec2d']) -> 'Vec2d':
        if isinstance(other, Vec2d):
            self.x *= other.x
            self.y *= other.y
        else:
            self.x *= other
            self.y *= other
        return self

    def __truediv__(self, other: Union[SupportsFloat, 'Vec2d']) -> 'Vec2d':
        if isinstance(other, Vec2d):
            return Vec2d(self.x / other.x, self.y / other.y)
        return Vec2d(self.x / other, self.y / other)

    def __itruediv__(self, other: Union[SupportsFloat, 'Vec2d']) -> 'Vec2d':
        if isinstance(other, Vec2d):
            self.x /= other.x
            self.y /= other.y
        else:
            self.x /= other
            self.y /= other
        return self

    def __add__(self, other: Union[SupportsFloat, 'Vec2d']) -> 'Vec2d':
        if isinstance(other, Vec2d):
            return Vec2d(self.x + other.x, self.y + other.y)
        return Vec2d(self.x + other, self.y + other)

    def __iadd__(self, other: Union[SupportsFloat, 'Vec2d']) -> 'Vec2d':
        if isinstance(other, Vec2d):
            self.x += other.x
            self.y += other.y
        else:
            self.x += other
            self.y += other
        return self

    def __sub__(self, other: Union[SupportsFloat, 'Vec2d']) -> 'Vec2d':
        if isinstance(other, Vec2d):
            return Vec2d(self.x - other.x, self.y - other.y)
        return Vec2d(self.x - other, self.y - other)

    def __isub__(self, other: Union[SupportsFloat, 'Vec2d']) -> 'Vec2d':
        if isinstance(other, Vec2d):
            self.x -= other.x
            self.y -= other.y
        else:
            self.x -= other
            self.y -= other
        return self

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Vec2d):
            return NotImplemented
        return math.isclose(self.x, other.x) and math.isclose(self.y, other.y)

    def __ne__(self, other: object) -> bool:
        if not isinstance(other, Vec2d):
            return NotImplemented
        return not (self == other)
