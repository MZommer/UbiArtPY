from functools import singledispatchmethod
import ctypes

STRIDE = 1

StringID_DLL = ctypes.cdll.LoadLibrary("./StringID.lib")
StringID_DLL.StrToCRC.restype = ctypes.c_uint32
StringID_DLL.StrToCRC.argtypes = ctypes.c_int, ctypes.c_char_p, ctypes.c_uint32

class StringID:
    InvalidId = 0xFFFFFFFF;
    FullStringTag = 0xEEEEEEEE;
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
            self._id = StringID_DLL.StrToCRC(ctypes.c_int(STRIDE), ctypes.c_char_p(string.encode('utf-8')), ctypes.c_uint32(len(string)))
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