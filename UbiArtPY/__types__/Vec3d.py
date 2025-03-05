import math
from typing import Union, SupportsFloat

import numpy

from .__base__ import float32
from ..Core import serializable_class


@serializable_class
class Vec3d:
    x: float32
    y: float32
    z: float32

    def __init__(self, x: SupportsFloat = 0, y: SupportsFloat = 0, z: SupportsFloat = 0) -> None:
        self.x = float32(x)
        self.y = float32(y)
        self.z = float32(z)

    def __str__(self) -> str:
        return f"x: {self.x}, y: {self.y}, z: {self.z}"

    def __repr__(self) -> str:
        return f"Vec3d(x={self.x}, y={self.y}, z={self.z})"

    def min(self, other: 'Vec3d') -> None:
        if not isinstance(other, Vec3d):
            raise TypeError("Argument must be a Vec3d")
        self.x = numpy.min(self.x, other.x)
        self.y = numpy.min(self.y, other.y)
        self.z = numpy.min(self.z, other.z)

    def max(self, other: 'Vec3d') -> None:
        if not isinstance(other, Vec3d):
            raise TypeError("Argument must be a Vec3d")
        self.x = numpy.max(self.x, other.x)
        self.y = numpy.max(self.y, other.y)
        self.z = numpy.max(self.z, other.z)

    def set_null(self) -> None:
        self.x = self.y = self.z = float32()

    def is_null(self) -> bool:
        return self.x == 0 and self.y == 0 and self.z == 0

    def is_nan(self) -> bool:
        return math.isnan(self.x) or math.isnan(self.y) or math.isnan(self.z)

    # Operators
    def __mul__(self, other: Union[SupportsFloat, 'Vec3d']) -> 'Vec3d':
        if isinstance(other, Vec3d):
            return Vec3d(self.x * other.x, self.y * other.y, self.z * other.z)
        return Vec3d(self.x * other, self.y * other, self.z * other)

    def __imul__(self, other: Union[SupportsFloat, 'Vec3d']) -> 'Vec3d':
        if isinstance(other, Vec3d):
            self.x *= other.x
            self.y *= other.y
            self.z *= other.z
        else:
            self.x *= other
            self.y *= other
            self.z *= other
        return self

    def __truediv__(self, other: Union[SupportsFloat, 'Vec3d']) -> 'Vec3d':
        if isinstance(other, Vec3d):
            return Vec3d(self.x / other.x, self.y / other.y, self.z / other.z)
        return Vec3d(self.x / other, self.y / other, self.z / other)

    def __itruediv__(self, other: Union[SupportsFloat, 'Vec3d']) -> 'Vec3d':
        if isinstance(other, Vec3d):
            self.x /= other.x
            self.y /= other.y
            self.z /= other.z
        else:
            self.x /= other
            self.y /= other
            self.z /= other
        return self

    def __add__(self, other: Union[SupportsFloat, 'Vec3d']) -> 'Vec3d':
        if isinstance(other, Vec3d):
            return Vec3d(self.x + other.x, self.y + other.y, self.z + other.z)
        return Vec3d(self.x + other, self.y + other, self.z + other)

    def __iadd__(self, other: Union[SupportsFloat, 'Vec3d']) -> 'Vec3d':
        if isinstance(other, Vec3d):
            self.x += other.x
            self.y += other.y
            self.z += other.z
        else:
            self.x += other
            self.y += other
            self.z += other
        return self

    def __sub__(self, other: Union[SupportsFloat, 'Vec3d']) -> 'Vec3d':
        if isinstance(other, Vec3d):
            return Vec3d(self.x - other.x, self.y - other.y, self.z - other.z)
        return Vec3d(self.x - other, self.y - other, self.z - other)

    def __isub__(self, other: Union[SupportsFloat, 'Vec3d']) -> 'Vec3d':
        if isinstance(other, Vec3d):
            self.x -= other.x
            self.y -= other.y
            self.z -= other.z
        else:
            self.x -= other
            self.y -= other
            self.z -= other
        return self

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Vec3d):
            return NotImplemented
        return (
                math.isclose(self.x, other.x) and
                math.isclose(self.y, other.y) and
                math.isclose(self.z, other.z)
        )

    def __ne__(self, other: object) -> bool:
        if not isinstance(other, Vec3d):
            return NotImplemented
        return not (self == other)
