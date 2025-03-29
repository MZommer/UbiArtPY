import abc
import warnings
from abc import ABC
from typing import (
    SupportsInt, SupportsFloat,
    SupportsAbs, SupportsRound, SupportsIndex,
    Any, Type, TypeVar
)

import numpy as np

warnings.filterwarnings('ignore')  # suppress numpy warnings eg. overflow in crc

T = TypeVar('T', bound='BaseType')


class BaseType(abc.ABC):
    """
    Base class for all custom types.

    This class provides common functionality for all numeric types, including
    representation, comparison, and basic arithmetic operations.
    """

    _value: T

    def __init__(self, value: Any = 0):
        self._value = self.dtype()(value)

    def __repr__(self):
        return f"{self.__class__.__name__}({self._value})"

    def __str__(self):
        return str(self._value)

    def __format__(self, format_spec):
        """
        Format the value according to the specified format string.

        Args:
            format_spec: Format specification string

        Returns:
            str: Formatted string representation
        """
        return format(self._value, format_spec)

    # Support for pickle protocol
    def __reduce__(self):
        """Support for pickle protocol."""
        return self.__class__, (self._value,)

    # Comparison operators
    def __eq__(self, other):
        if isinstance(other, BaseType):
            return self._value == other._value
        return self._value == other

    def __lt__(self, other):
        if isinstance(other, BaseType):
            return self._value < other._value
        return self._value < other

    def __gt__(self, other):
        if isinstance(other, BaseType):
            return self._value > other._value
        return self._value > other

    def __le__(self, other):
        if isinstance(other, BaseType):
            return self._value <= other._value
        return self._value <= other

    def __ge__(self, other):
        if isinstance(other, BaseType):
            return self._value >= other._value
        return self._value >= other

    def __ne__(self, other):
        if isinstance(other, BaseType):
            return self._value != other._value
        return self._value != other

    def __hash__(self):
        return hash((self.__class__, self._value))

    # Arithmetic operators
    def __add__(self, other):
        if isinstance(other, BaseType):
            return self.__class__(self._value + other._value)
        return self.__class__(self._value + other)

    def __radd__(self, other):
        return self.__class__(other + self._value)

    def __sub__(self, other):
        if isinstance(other, BaseType):
            return self.__class__(self._value - other._value)
        return self.__class__(self._value - other)

    def __rsub__(self, other):
        return self.__class__(other - self._value)

    def __mul__(self, other):
        if isinstance(other, BaseType):
            return self.__class__(self._value * other._value)
        return self.__class__(self._value * other)

    def __rmul__(self, other):
        return self.__class__(other * self._value)

    def __truediv__(self, other):
        if isinstance(other, BaseType):
            return self.__class__(self._value / other._value)
        return self.__class__(self._value / other)

    def __rtruediv__(self, other):
        return self.__class__(other / self._value)

    def __floordiv__(self, other):
        if isinstance(other, BaseType):
            return self.__class__(self._value // other._value)
        return self.__class__(self._value // other)

    def __rfloordiv__(self, other):
        return self.__class__(other // self._value)

    def __mod__(self, other):
        if isinstance(other, BaseType):
            return self.__class__(self._value % other._value)
        return self.__class__(self._value % other)

    def __rmod__(self, other):
        return self.__class__(other % self._value)

    def __pow__(self, other):
        if isinstance(other, BaseType):
            return self.__class__(self._value ** other._value)
        return self.__class__(self._value ** other)

    def __rpow__(self, other):
        return self.__class__(other ** self._value)

    def __neg__(self):
        return self.__class__(-self._value)

    def __pos__(self):
        return self.__class__(+self._value)

    @classmethod
    def get_sizeof(cls) -> int:
        """
        Return the size (in bytes) of the type.

        Returns:
            int: Size in bytes

        Examples:
            >>> int32.get_sizeof()
            4
            >>> float64.get_sizeof()
            8
        """
        return np.dtype(cls._dtype()).itemsize

    @classmethod
    def get_type_format(cls) -> str:
        """
        Return the format character for the type.

        Returns:
            str: Format character

        Examples:
            >>> int32.get_type_format()
            'i'
            >>> float64.get_type_format()
            'd'
        """
        return cls._dtype().char

    @classmethod
    @abc.abstractmethod
    def _dtype(cls) -> np.dtype:
        """Return the NumPy dtype for the type."""
        raise NotImplementedError

    @classmethod
    def dtype(cls) -> np.dtype:
        """
        Return the NumPy dtype for the type.

        Returns:
            np.dtype: NumPy data type

        Examples:
            >>> int32.dtype()
            dtype('int32')
        """
        return cls._dtype()

    @classmethod
    def from_numpy(cls: Type[T], value: Any) -> T:
        """
        Create instance from NumPy type.

        Args:
            value: Value to convert

        Returns:
            Instance of the class

        Examples:
            >>> int32.from_numpy(np.int32(42))
            int32(42)
        """
        return cls(value)

    def as_numpy(self):
        """
        Convert to NumPy type.

        Returns:
            NumPy scalar

        Examples:
            >>> x = int32(42)
            >>> x.as_numpy()
            42
            >>> type(x.as_numpy())
            <class 'numpy.int32'>
        """
        return np.array([self._value], dtype=self._dtype())[0]

    def as_type(self, target_type: Type[T]) -> T:
        """
        Convert to another custom type.

        Args:
            target_type: Target type class

        Returns:
            Instance of target_type

        Examples:
            >>> x = int32(42)
            >>> x.as_type(float32)
            float32(42.0)
        """
        if not issubclass(target_type, BaseType):
            raise TypeError(f"{target_type} is not a valid target type")
        return target_type(self._value)

    @classmethod
    def array(cls, values):
        """
        Create NumPy array with the proper dtype.

        Args:
            values: Values to convert

        Returns:
            np.ndarray: NumPy array with the dtype of the class

        Examples:
            >>> int32.array([1, 2, 3])
            array([1, 2, 3], dtype=int32)
        """
        return np.array(values, dtype=cls._dtype())


class BaseInt(
    BaseType,
    SupportsInt,
    SupportsAbs,
    SupportsRound,
    SupportsIndex, ABC
):
    """
    Base class for integer types.

    This class provides common functionality for all integer types,
    including integer-specific operations and validation.
    """

    def __int__(self):
        return int(self._value)

    def __index__(self):
        return int(self)

    def __round__(self, digits: int = None):
        return round(self._value, digits)

    def __abs__(self):
        return self.__class__(abs(self._value))

    # Format as string in different bases
    def __hex__(self):
        """Return a hexadecimal string representation."""
        return hex(int(self._value))

    def __oct__(self):
        """Return an octal string representation."""
        return oct(int(self._value))

    def __bin__(self):
        """Return a binary string representation."""
        return bin(int(self._value))

    # Bitwise operations
    def __and__(self, other):
        if isinstance(other, BaseType):
            return self.__class__(self._value & other._value)
        return self.__class__(self._value & other)

    def __rand__(self, other):
        return self.__class__(other & self._value)

    def __or__(self, other):
        if isinstance(other, BaseType):
            return self.__class__(self._value | other._value)
        return self.__class__(self._value | other)

    def __ror__(self, other):
        return self.__class__(other | self._value)

    def __xor__(self, other):
        if isinstance(other, BaseType):
            return self.__class__(self._value ^ other._value)
        return self.__class__(self._value ^ other)

    def __rxor__(self, other):
        return self.__class__(other ^ self._value)

    def __lshift__(self, other):
        if isinstance(other, BaseType):
            return self.__class__(self._value << other._value)
        return self.__class__(self._value << other)

    def __rlshift__(self, other):
        return self.__class__(other << self._value)

    def __rshift__(self, other):
        if isinstance(other, BaseType):
            return self.__class__(self._value >> other._value)
        return self.__class__(self._value >> other)

    def __rrshift__(self, other):
        return self.__class__(other >> self._value)

    def __invert__(self):
        return self.__class__(~self._value)

    def __mul__(self, other):
        if isinstance(other, BaseType):
            return self.__class__(self._value * other._value)
        if isinstance(other, float):
            return other.__class__(self._value * other)
        if isinstance(other, int):
            return self.__class__(self._value * other)

        return self._value * other

    def __rmul__(self, other):
        return self * other

    def __imul__(self, other):
        self._value = self * other
        return self

    @classmethod
    def is_valid(cls, value: int) -> bool:
        """
        Check if the value is within the valid range for the type.

        Args:
            value: Value to check

        Returns:
            bool: True if the value is within range, False otherwise

        Examples:
            >>> int8.is_valid(127)
            True
            >>> int8.is_valid(128)
            False
        """
        info = np.iinfo(cls._dtype())
        return info.min <= value <= info.max

    @classmethod
    def safe_cast(cls: Type[T], value: int) -> T:
        """
        Convert the value to the type, raising an error if out of range.

        Args:
            value: Value to convert

        Returns:
            Instance of the class

        Raises:
            ValueError: If value is out of range

        Examples:
            >>> int8.safe_cast(127)
            int8(127)
            >>> int8.safe_cast(128)
            Traceback (most recent call last):
            ...
            ValueError: Value 128 is out of range for int8
        """
        if not cls.is_valid(value):
            raise ValueError(f"Value {value} is out of range for {cls.__name__}")
        return cls(value)

    @classmethod
    def min_value(cls) -> int:
        """
        Return the minimum value for this type.

        Returns:
            int: Minimum value

        Examples:
            >>> int8.min_value()
            -128
        """
        return np.iinfo(cls._dtype()).min

    @classmethod
    def max_value(cls) -> int:
        """
        Return the maximum value for this type.

        Returns:
            int: Maximum value

        Examples:
            >>> int8.max_value()
            127
        """
        return np.iinfo(cls._dtype()).max


class BaseFloat(
    BaseType,
    SupportsFloat,
    SupportsAbs,
    SupportsRound, ABC
):
    """
    Base class for floating-point types.

    This class provides common functionality for all floating-point types,
    including float-specific operations and validation.
    """

    def __float__(self):
        return float(self._value)

    def __abs__(self):
        return self.__class__(abs(self._value))

    def __round__(self, digits: int = None):
        return round(self._value, digits)

    # Support for special float methods
    def is_integer(self):
        """Check if the float value is an integer."""
        return float(self._value).is_integer()

    def hex(self):
        """Return a hexadecimal representation of a float."""
        return float(self._value).hex()

    @classmethod
    def fromhex(cls, s):
        """Class method to return a float constructed from a hexadecimal string."""
        return cls(float.fromhex(s))

    @classmethod
    def is_valid(cls, value: float) -> bool:
        """
        Check if the value is within the valid range for the type.

        Args:
            value: Value to check

        Returns:
            bool: True if the value is within range, False otherwise
        """
        info = np.finfo(cls._dtype())
        return info.min <= value <= info.max or np.isnan(value)

    @classmethod
    def safe_cast(cls: Type[T], value: float) -> T:
        """
        Convert the value to the type, raising an error if out of range.

        Args:
            value: Value to convert

        Returns:
            Instance of the class

        Raises:
            ValueError: If value is out of range
        """
        if not cls.is_valid(value):
            raise ValueError(f"Value {value} is out of range for {cls.__name__}")
        return cls(value)

    @classmethod
    def min_value(cls) -> float:
        """
        Return the minimum value for this type.

        Returns:
            float: Minimum value
        """
        return np.finfo(cls._dtype()).min

    @classmethod
    def max_value(cls) -> float:
        """
        Return the maximum value for this type.

        Returns:
            float: Maximum value
        """
        return np.finfo(cls._dtype()).max

    @classmethod
    def epsilon(cls) -> float:
        """
        Return the smallest positive value for this type.

        Returns:
            float: Smallest positive value
        """
        return np.finfo(cls._dtype()).eps

    @classmethod
    def infinity(cls) -> T:
        """
        Return positive infinity for this type.

        Returns:
            Instance representing infinity
        """
        return cls(np.inf)

    @classmethod
    def negative_infinity(cls) -> T:
        """
        Return negative infinity for this type.

        Returns:
            Instance representing negative infinity
        """
        return cls(-np.inf)

    @classmethod
    def nan(cls) -> T:
        """
        Return Not-a-Number for this type.

        Returns:
            Instance representing NaN
        """
        return cls(np.nan)

    def is_nan(self) -> bool:
        """
        Check if the value is NaN.

        Returns:
            bool: True if the value is NaN, False otherwise
        """
        return np.isnan(self._value)

    def is_infinite(self) -> bool:
        """
        Check if the value is infinite.

        Returns:
            bool: True if the value is infinite, False otherwise
        """
        return np.isinf(self._value)

    def is_finite(self) -> bool:
        """
        Check if the value is finite.

        Returns:
            bool: True if the value is finite, False otherwise
        """
        return np.isfinite(self._value)


# Integer types
class int8(BaseInt):
    """8-bit signed integer (-128 to 127)."""

    @classmethod
    def _dtype(cls) -> np.dtype:
        return np.int8


class uint8(BaseInt):
    """8-bit unsigned integer (0 to 255)."""

    @classmethod
    def _dtype(cls) -> np.dtype:
        return np.uint8


class int16(BaseInt):
    """16-bit signed integer (-32,768 to 32,767)."""

    @classmethod
    def _dtype(cls) -> np.dtype:
        return np.int16


class uint16(BaseInt):
    """16-bit unsigned integer (0 to 65,535)."""

    @classmethod
    def _dtype(cls) -> np.dtype:
        return np.uint16


class int32(BaseInt):
    """32-bit signed integer (-2,147,483,648 to 2,147,483,647)."""

    @classmethod
    def _dtype(cls) -> np.dtype:
        return np.int32


class uint32(BaseInt):
    """32-bit unsigned integer (0 to 4,294,967,295)."""

    @classmethod
    def _dtype(cls) -> np.dtype:
        return np.uint32


class int64(BaseInt):
    """64-bit signed integer (-9,223,372,036,854,775,808 to 9,223,372,036,854,775,807)."""

    @classmethod
    def _dtype(cls) -> np.dtype:
        return np.int64


class uint64(BaseInt):
    """64-bit unsigned integer (0 to 18,446,744,073,709,551,615)."""

    @classmethod
    def _dtype(cls) -> np.dtype:
        return np.uint64


# Floating-point types
class float16(BaseFloat):
    """
    16-bit floating-point number.

    Also known as "half-precision" float.
    Approximate range: ±6.55×10^4, with ~3.3 decimal digits of precision.
    """

    @classmethod
    def _dtype(cls) -> np.dtype:
        return np.float16


class float32(BaseFloat):
    """
    32-bit floating-point number.

    Also known as "single-precision" float.
    Approximate range: ±3.4×10^38, with ~7 decimal digits of precision.
    """

    @classmethod
    def _dtype(cls) -> np.dtype:
        return np.float32


class float64(BaseFloat):
    """
    64-bit floating-point number.

    Also known as "double-precision" float.
    Approximate range: ±1.8×10^308, with ~15 decimal digits of precision.
    """

    @classmethod
    def _dtype(cls) -> np.dtype:
        return np.float64


# Boolean type
class bbool(BaseType):
    """
    Boolean type.

    Represents True or False values.
    """

    def __init__(self, value=False):
        self._value = bool(value)

    @classmethod
    def _dtype(cls) -> np.dtype:
        return np.bool_

    def __bool__(self):
        return self._value

    def __int__(self):
        return 1 if self._value else 0

    def __float__(self):
        return 1.0 if self._value else 0.0

    def __format__(self, format_spec):
        """Format the boolean value according to the format specification."""
        # Most format specs don't make sense for booleans, but we'll handle them anyway
        if not format_spec:
            return str(self._value)
        return format(self._value, format_spec)

    # Logical operations
    def __and__(self, other):
        if isinstance(other, BaseType):
            return self.__class__(self._value and bool(other._value))
        return self.__class__(self._value and bool(other))

    def __rand__(self, other):
        return self.__class__(bool(other) and self._value)

    def __or__(self, other):
        if isinstance(other, BaseType):
            return self.__class__(self._value or bool(other._value))
        return self.__class__(self._value or bool(other))

    def __ror__(self, other):
        return self.__class__(bool(other) or self._value)

    def __xor__(self, other):
        if isinstance(other, BaseType):
            return self.__class__(self._value != bool(other._value))
        return self.__class__(self._value != bool(other))

    def __rxor__(self, other):
        return self.__class__(bool(other) != self._value)

    def __invert__(self):
        return self.__class__(not self._value)


# Type aliases
byte = int8
ubyte = uint8
short = int16
ushort = uint16
int_t = int32  # Changed from _int to int_t to avoid confusion
uint = uint32
long = int64
ulong = uint64
half = float16
single = float32
double = float64

# List of all base types
BaseTypes = (
    int8, uint8, int16, uint16, uint32, int32,
    int64, uint64, float16, float32, float64, bbool
)
