from functools import singledispatchmethod

STRIDE = 1

def UInt32(value: int) -> int:
    '''Cast python int to uint32'''
    return value & 0xFFFFFFFF

def ToUp(char: int) -> int:
    if char >= 0x61 and char <= 0x7a:
        char -= 0x20
    return char

def mix(a: int, b: int, c: int) -> list[int, int, int]:
    a = UInt32((a - b - c) ^ (c >> 13))
    b = UInt32((b - c - a) ^ (a << 8))
    c = UInt32((c - a - b) ^ (b >> 13))
    a = UInt32((a - b - c) ^ (c >> 12))
    b = UInt32((b - c - a) ^ (a << 16))
    c = UInt32((c - a - b) ^ (b >> 5))
    a = UInt32((a - b - c) ^ (c >> 3))
    b = UInt32((b - c - a) ^ (a << 10))
    c = UInt32((c - a - b) ^ (b >> 15))
    # value should be referenced, but this is not possible in python
    return a, b, c

def StrToCRC(_stride: int, _str: str, _len: int) -> int:
    if isinstance(_str, str):
        _str = _str.encode("utf-8")
    
    # Set up the internal state #
    Len: int = _len
    len: int = Len
    a: int = 0x9e3779b9 # the golden ratio; an arbitrary value
    b: int = a
    c: int = 0
    
    #  handle most of the key
    while len >= 12:
        a += UInt32(ToUp(_str[0 * _stride]) + (ToUp(_str[1 * _stride]) << 8) + (ToUp(_str[2 * _stride]) << 16) + (ToUp(_str[3 * _stride]) << 24))
        b += UInt32(ToUp(_str[4 * _stride]) + (ToUp(_str[5 * _stride]) << 8) + (ToUp(_str[6 * _stride]) << 16) + (ToUp(_str[7 * _stride]) << 24))
        c += UInt32(ToUp(_str[8 * _stride]) + (ToUp(_str[9 * _stride]) << 8) + (ToUp(_str[10 * _stride]) << 16) + (ToUp(_str[11 * _stride]) << 24))
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
    InvalidId = 0xFFFFFFFF
    FullStringTag = 0xEEEEEEEE
    _id = InvalidId
    _string: str = ""

    # Constructors and Converters
    @singledispatchmethod
    def __init__(self, value):
        pass # TODO: CHECK?
    @__init__.register
    def _(self, string: str):
        if string:
            self._string = string
            self._id = StrToCRC(STRIDE, string, len(string))
        else:
            self._id = self.InvalidId
    @__init__.register
    def _(self, value: int):
        self._id = value

    def __int__(self) -> int:
        return int(self._id)
    def __str__(self):
        if self._string:
            return self._string
        return f"{self._id:x}"

    def isValid(self) -> bool:
        return self._id != self.InvalidId
    
    def getHashCode(self) -> int:
        return self._id
