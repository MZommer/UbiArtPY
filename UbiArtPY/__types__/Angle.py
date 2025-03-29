import math
from typing import SupportsFloat, Self

from .__base__ import float32
from ..Core.SerializableClass import serializable_class


@serializable_class
class Angle:
    value: float32

    def __init__(self, angle: SupportsFloat, degree: bool = False):
        angle = float32(angle)  # Cast value to float
        if degree:
            self.set_degree(angle)
        else:
            self.set_radian(angle)

    def __str__(self) -> str:
        return str(self.value)

    def __repr__(self) -> str:
        return f"Angle({self})"

    def __eq__(self, other: Self) -> bool:
        return math.isclose(self.value, other.value) or math.isclose(self.value, other)

    def __ne__(self, other: Self) -> bool:
        return not self.__eq__(other)

    def __add__(self, other: Self) -> Self:
        if isinstance(other, Angle):
            return Angle(self.value + other.value)
        return Angle(self.value + other)

    __radd__ = __add__

    def __iadd__(self, other: Self) -> Self:
        if isinstance(other, Angle):
            self.value += other.value
        else:
            self.value += other
        return self

    def __sub__(self, other: Self) -> Self:
        if isinstance(other, Angle):
            return Angle(self.value - other.value)
        return Angle(self.value - other)

    __rsub__ = __sub__

    def __isub__(self, other: Self) -> Self:
        if isinstance(other, Angle):
            self.value -= other.value
        else:
            self.value -= other
        return self

    def __mul__(self, other: Self) -> Self:
        if isinstance(other, Angle):
            return Angle(self.value * other.value)
        return Angle(self.value * other)

    __rmul__ = __mul__

    def __imul__(self, other: Self) -> Self:
        if isinstance(other, Angle):
            self.value *= other.value
        else:
            self.value *= other
        return self

    def __truediv__(self, other: Self) -> Self:
        if isinstance(other, Angle):
            return Angle(self.value / other.value)
        return Angle(self.value / other)

    __rtruediv__ = __truediv__

    def __itruediv__(self, other: Self) -> Self:
        if isinstance(other, Angle):
            self.value /= other.value
        else:
            self.value /= other
        return self

    def __floordiv__(self, other: Self) -> Self:
        if isinstance(other, Angle):
            return Angle(self.value // other.value)
        return Angle(self.value // other)

    __rfloordiv__ = __floordiv__

    def __neg__(self) -> Self:
        return Angle(~self.value)

    __invert__ = __neg__

    def set_degree(self, angle: SupportsFloat):
        self.value = float32(float(angle) * math.pi / 180)

    def set_radian(self, angle: float32):
        self.value = angle

    def to_degree(self) -> float32:
        return float32(180.0 * self.value / math.pi)

    def to_radian(self) -> float32:
        return self.value
