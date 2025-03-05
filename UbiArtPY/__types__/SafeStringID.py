from .String8 import String8
from .StringID import StringID


class SafeStringID:
    _string8: String8
    _stringID: StringID

    def __init__(self, string: String8 = ""):
        self._string8 = String8(string)
        self._stringID = StringID(string)

    def __str__(self) -> str:
        return self._string8

    def __int__(self) -> int:
        return int(self._stringID)

    def __eq__(self, __value) -> bool:
        if isinstance(__value, SafeStringID):
            return self._string8 == __value._string8 and self._stringID == __value._stringID
        if isinstance(__value, StringID):
            return self._stringID == __value
        if isinstance(__value, str):
            return self._string8 == __value
        return False

    def get_hash_code(self) -> StringID:
        return self._stringID.get_hash_code()
