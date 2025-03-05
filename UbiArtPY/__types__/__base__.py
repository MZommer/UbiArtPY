import abc
import warnings
from typing import (
    SupportsInt, SupportsFloat,
    SupportsAbs, SupportsRound, SupportsIndex,
)

import numpy

warnings.filterwarnings('ignore')  # suppress numpy warnings eg. overflow in crc


class BaseType(abc.ABC):
    """Base class for all custom numeric types."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @classmethod
    def get_sizeof(cls) -> int:
        """Return the size (in bytes) of the type."""
        return numpy.dtype(cls).itemsize

    @classmethod
    def get_type_format(cls) -> str:
        """Return the format character for the type."""
        return numpy.dtype(cls).char

    @classmethod
    def dtype(cls) -> numpy.dtype:
        """Return the NumPy dtype for the type."""
        return numpy.dtype(cls)


class BaseInt(
    BaseType,
    SupportsInt,
    SupportsAbs,
    SupportsRound,
    SupportsIndex,
):
    """Base class for integer types."""

    def __index__(self):
        return self

    def __round__(self, digits: int = None):
        return round(self, digits)

    def __abs__(self):
        return abs(self)

    def __int__(self):
        return self

    @classmethod
    def is_valid(cls, value: int) -> bool:
        """Check if the value is within the valid range for the type."""
        info = numpy.iinfo(cls)
        return info.min <= value <= info.max

    @classmethod
    def safe_cast(cls, value: int) -> 'BaseInt':
        """Convert the value to the type, raising an error if out of range."""
        if not cls.is_valid(value):
            raise ValueError(f"Value {value} is out of range for {cls.__name__}")
        return cls(value)

    def __instancecheck__(self, instance: object) -> bool:
        return isinstance(instance, int)

    def __subclasscheck__(self, subclass: type) -> bool:
        return issubclass(subclass, int)


class BaseFloat(
    BaseType,
    SupportsFloat,
    SupportsAbs,
    SupportsRound,
):
    """Base class for floating-point types."""

    def __abs__(self):
        return abs(self)

    def __round__(self, digits: int = None):
        return round(self, digits)

    def __float__(self):
        return self

    @classmethod
    def is_valid(cls, value: float) -> bool:
        """Check if the value is within the valid range for the type."""
        info = numpy.finfo(cls)
        return info.min <= value <= info.max

    @classmethod
    def safe_cast(cls, value: float) -> 'BaseFloat':
        """Convert the value to the type, raising an error if out of range."""
        if not cls.is_valid(value):
            raise ValueError(f"Value {value} is out of range for {cls.__name__}")
        return cls(value)

    def __instancecheck__(self, instance: object) -> bool:
        return isinstance(instance, float)

    def __subclasscheck__(self, subclass: type) -> bool:
        return issubclass(subclass, float)


# Integer types
class int8(BaseInt, numpy.int8):
    """8-bit signed integer."""


class uint8(BaseInt, numpy.uint8):
    """8-bit unsigned integer."""


class int16(BaseInt, numpy.int16):
    """16-bit signed integer."""


class uint16(BaseInt, numpy.uint16):
    """16-bit unsigned integer."""


class int32(BaseInt, numpy.int32):
    """32-bit signed integer."""


class uint32(BaseInt, numpy.uint32):
    """32-bit unsigned integer."""


class int64(BaseInt, numpy.int64):
    """64-bit signed integer."""


class uint64(BaseInt, numpy.uint64):
    """64-bit unsigned integer."""


# Floating-point types
class float16(BaseFloat, numpy.float16):
    """16-bit floating-point number."""


class float32(BaseFloat, numpy.float32):
    """32-bit floating-point number."""


class float64(BaseFloat, numpy.float64):
    """64-bit floating-point number."""


# Boolean type
class bbool(BaseType, numpy.bool_):
    """Boolean type."""


# Type aliases
byte = int8
ubyte = uint8
short = int16
ushort = uint16
_int = int32
uint = uint32
long = int64
ulong = uint64
half = float16
single = float32
double = float64

# List of all base types
BaseTypes = int8, uint8, int16, uint16, uint32, int32, float32, float64, bbool, str, list, dict, tuple
