from .__base__ import uint32
# from ..Core import ArchiveMemory  # circular import
from .String8 import String8

STRIDE = 1

def uint32_cast(value: int) -> uint32:
    '''Cast python int to uint32'''
    return uint32(value & 0xFFFFFFFF)

def ToUp(char: uint32) -> uint32:
    if char >= 0x61 and char <= 0x7a:
        char -= 0x20
    return char

def mix(a: uint32, b: uint32, c: uint32) -> list[uint32, uint32, uint32]:
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

def StrToCRC(_stride: uint32, _str: str, _len: uint32) -> uint32:
    if isinstance(_str, str):
        _str = _str.encode("utf-8")
    
    # Set up the internal state #
    Len: uint32 = _len
    len: uint32 = Len
    a: uint32 = 0x9e3779b9 # the golden ratio; an arbitrary value
    b: uint32 = a
    c: uint32 = 0
    
    #  handle most of the key
    while len >= 12:
        a += uint32_cast(ToUp(_str[0 * _stride]) + (ToUp(_str[1 * _stride]) << 8) + (ToUp(_str[2 * _stride]) << 16) + (ToUp(_str[3 * _stride]) << 24))
        b += uint32_cast(ToUp(_str[4 * _stride]) + (ToUp(_str[5 * _stride]) << 8) + (ToUp(_str[6 * _stride]) << 16) + (ToUp(_str[7 * _stride]) << 24))
        c += uint32_cast(ToUp(_str[8 * _stride]) + (ToUp(_str[9 * _stride]) << 8) + (ToUp(_str[10 * _stride]) << 16) + (ToUp(_str[11 * _stride]) << 24))
        a, b, c = mix(a, b, c)
        
        _str = _str[12 * _stride:] # substr
        len -= 12
    
    # handle the last 11 bytes
    c += Len
    # Now we will implement the behaivour of the switch statement
    # in a different way, because of the lack of references (and switch) in python
    if len > 0: # all the case statements fall through
        if len >= 11: c += ToUp(_str[10 * _stride]) << 24
        if len >= 10: c += ToUp(_str[9 * _stride]) << 16
        if len >= 9: c += ToUp(_str[8 * _stride]) << 8
        if len >= 8: b += ToUp(_str[7 * _stride]) << 24
        if len >= 7: b += ToUp(_str[6 * _stride]) << 16
        if len >= 6: b += ToUp(_str[5 * _stride]) << 8
        if len >= 5: b += ToUp(_str[4 * _stride])
        if len >= 4: a += ToUp(_str[3 * _stride]) << 24
        if len >= 3: a += ToUp(_str[2 * _stride]) << 16
        if len >= 2: a += ToUp(_str[1 * _stride]) << 8
        if len >= 1: a += ToUp(_str[0 * _stride])
    
    a, b, c = mix(a, b, c)
    return c

class StringID:
    InvalidId: uint32 = uint32(0xFFFFFFFF)
    FullStringTag: uint32 = uint32(0xEEEEEEEE)
    _id: uint32 = InvalidId
    _string: str = ""

    # Constructors and Converters
    def __init__(self, value: String8 | uint32):
        if isinstance(value, int):
            self._id = uint32(value)
        elif isinstance(value, StringID):
            self._id = value._id
            self._string = value._string
        elif value:
            self._string = String8(value)
            self._id = StrToCRC(STRIDE, self._string, len(self._string))
        else:
            self._id = self.InvalidId
    
    def __eq__(self, other: 'StringID') -> bool:
        if isinstance(other, StringID):
            return self._id == other._id
    
    def __hash__(self):
        return int(self._id)
    
    def __int__(self) -> uint32:
        return uint32(self._id)
    
    def __str__(self):
        if self._string:
            return self._string
        return f"{self._id:x}"

    def __repr__(self):
        return f"StringID({self})"
    
    def isValid(self) -> bool:
        return self._id != self.InvalidId
    
    def GetHashCode(self) -> uint32:
        return self._id
    
    def serialize(self, _archive: "ArchiveMemory"):
        self._id = _archive.serialize(self._id)
