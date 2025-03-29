import warnings
from functools import lru_cache
from typing import Tuple, Optional, Union

# from ..Core.SerializableClass import ArchiveMemory  # circular import
from .String8 import String8
from .__base__ import uint32

# Try to import Numba, fall back to standard implementation if not available
try:
    from numba import njit
except ImportError:
    warnings.warn("[StringID] Numba not available - falling back to slower pure Python implementation")


    def njit(func):
        return func

STRIDE = 1


@njit
def uint32_cast(value: int) -> int:
    return value & 0xFFFFFFFF


@njit
def to_up(char: int) -> int:
    if 0x61 <= char <= 0x7a:
        char -= 0x20
    return char


@njit
def mix(a: int, b: int, c: int) -> Tuple[int, int, int]:
    a = uint32_cast((a - b - c) ^ (c >> 13))
    b = uint32_cast((b - c - a) ^ (a << 8))
    c = uint32_cast((c - a - b) ^ (b >> 13))
    a = uint32_cast((a - b - c) ^ (c >> 12))
    b = uint32_cast((b - c - a) ^ (a << 16))
    c = uint32_cast((c - a - b) ^ (b >> 5))
    a = uint32_cast((a - b - c) ^ (c >> 3))
    b = uint32_cast((b - c - a) ^ (a << 10))
    c = uint32_cast((c - a - b) ^ (b >> 15))
    # value should be referenced, but this is not possible in python
    return a, b, c


@njit
def str_to_crc(_stride: int, _string: bytes, _length: int) -> int:
    # Set up the internal state #
    length = _length
    a = 0x9e3779b9  # the golden ratio; an arbitrary value
    b = a
    c = 0

    #  handle most of the key
    while length >= 12:
        a += uint32_cast(
            to_up(_string[0 * _stride]) + (to_up(_string[1 * _stride]) << 8) + (to_up(_string[2 * _stride]) << 16) + (
                    to_up(_string[3 * _stride]) << 24))
        b += uint32_cast(
            to_up(_string[4 * _stride]) + (to_up(_string[5 * _stride]) << 8) + (to_up(_string[6 * _stride]) << 16) + (
                    to_up(_string[7 * _stride]) << 24))
        c += uint32_cast(
            to_up(_string[8 * _stride]) + (to_up(_string[9 * _stride]) << 8) + (to_up(_string[10 * _stride]) << 16) + (
                    to_up(_string[11 * _stride]) << 24))
        a, b, c = mix(a, b, c)

        _string = _string[12 * _stride:]
        length -= 12

    # handle the last 11 bytes
    c += _length
    # Now we will implement the behaviour of the switch statement
    # in a different way, because of the lack of references (and switch) in python
    if length > 0:  # all the case statements fall through
        if length >= 11: c += to_up(_string[10 * _stride]) << 24
        if length >= 10: c += to_up(_string[9 * _stride]) << 16
        if length >= 9: c += to_up(_string[8 * _stride]) << 8
        if length >= 8: b += to_up(_string[7 * _stride]) << 24
        if length >= 7: b += to_up(_string[6 * _stride]) << 16
        if length >= 6: b += to_up(_string[5 * _stride]) << 8
        if length >= 5: b += to_up(_string[4 * _stride])
        if length >= 4: a += to_up(_string[3 * _stride]) << 24
        if length >= 3: a += to_up(_string[2 * _stride]) << 16
        if length >= 2: a += to_up(_string[1 * _stride]) << 8
        if length >= 1: a += to_up(_string[0 * _stride])

    a, b, c = mix(a, b, c)
    return c


@lru_cache(maxsize=1024)
def str_to_crc_cached(_stride: int, _string: bytes, _length: int) -> int:
    return str_to_crc(_stride, _string, _length)


class StringID:
    InvalidId: uint32 = uint32(0xFFFFFFFF)
    FullStringTag: uint32 = uint32(0xEEEEEEEE)
    id: uint32 = InvalidId
    string: str = ""

    # Constructors and Converters
    def __init__(self, value: Optional[Union["StringID", str, int]] = None):
        if isinstance(value, int):
            self.id = uint32(value)
        elif isinstance(value, StringID):
            self.id = value.id
            self.string = value.string
        elif value:
            self.string = String8(value)
            self.id = uint32(str_to_crc(STRIDE, self.string.encode("utf-8"), len(self.string)))
        else:
            self.id = self.InvalidId

    def __eq__(self, other: 'StringID') -> bool:
        if isinstance(other, StringID):
            return self.id == other.id
        return self.id == other

    def __hash__(self) -> int:
        return int(self.id)

    def __int__(self) -> int:
        return int(self.id)

    def __str__(self) -> str:
        if self.string:
            return self.string
        return f"{self.id:x}"

    def __repr__(self) -> str:
        return f"StringID({self})"

    def is_valid(self) -> bool:
        return self.id != self.InvalidId

    def get_hash_code(self) -> uint32:
        return self.id

    def get_value(self):
        return str(self)

    def serialize(self, _archive: "ArchiveMemory"):
        self.id = _archive.serialize(self.id)
