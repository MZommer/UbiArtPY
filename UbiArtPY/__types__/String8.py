import base64
from typing import Union, List, Optional, Iterable, Any

from .__base__ import uint32


class String8(str):  # Inherits from str for compatibility
    state: str  # Current state

    def __init__(self, value: Any = "") -> None:
        self.state = str(value)

    def __str__(self) -> str:
        return self.state

    def __repr__(self) -> str:
        return f"String8({self.state})"

    def __getitem__(self, key: Union[int, slice]) -> "String8":
        return String8(self.state[key])

    def __contains__(self, item: str) -> bool:
        return item in self.state

    def __add__(self, other: Union[str, "String8"]) -> "String8":
        return String8(self.state + str(other))

    __radd__ = __add__

    def __iadd__(self, other: Union[str, "String8"]) -> "String8":
        self.state += str(other)
        return self

    def __mul__(self, other: int) -> "String8":
        return String8(self.state * other)

    __rmul__ = __mul__

    def __imul__(self, other: int) -> "String8":
        self.state *= other
        return self

    def __eq__(self, other: object) -> bool:
        return self.state == str(other)

    def __ne__(self, other: object) -> bool:
        return self.state != str(other)

    def __hash__(self) -> int:
        return hash(self.state)

    def lower(self) -> "String8":
        """Cached lowercase version of the string."""
        return String8(self.state.lower())

    def upper(self) -> "String8":
        """Cached uppercase version of the string."""
        return String8(self.state.upper())

    def stripped(self) -> "String8":
        """Cached stripped version of the string."""
        return String8(self.state.strip())

    # String methods
    def strip(self, chars: Optional[str] = None) -> "String8":
        return String8(self.state.strip(chars))

    def split(self, sep: Optional[str] = None, maxsplit: int = -1) -> List["String8"]:
        return [String8(s) for s in self.state.split(sep, maxsplit)]

    def rsplit(self, sep: Optional[str] = None, maxsplit: int = -1) -> List["String8"]:
        return [String8(s) for s in self.state.rsplit(sep, maxsplit)]

    def replace(self, old: str, new: str, count: int = -1) -> "String8":
        return String8(self.state.replace(old, new, count))

    def startswith(self, prefix: Union[str, tuple], start: Optional[int] = None, end: Optional[int] = None) -> bool:
        return self.state.startswith(prefix, start, end)

    def endswith(self, suffix: Union[str, tuple], start: Optional[int] = None, end: Optional[int] = None) -> bool:
        return self.state.endswith(suffix, start, end)

    def find(self, sub: str, start: int = 0, end: Optional[int] = None) -> int:
        return self.state.find(sub, start, end)

    def index(self, sub: str, start: int = 0, end: Optional[int] = None) -> int:
        return self.state.index(sub, start, end)

    def isalnum(self) -> bool:
        return self.state.isalnum()

    def isalpha(self) -> bool:
        return self.state.isalpha()

    def isdigit(self) -> bool:
        return self.state.isdigit()

    def islower(self) -> bool:
        return self.state.islower()

    def isupper(self) -> bool:
        return self.state.isupper()

    def isspace(self) -> bool:
        return self.state.isspace()

    def join(self, iterable: Iterable[str]) -> "String8":
        return String8(self.state.join(iterable))

    # Format methods
    def format(self, *args, **kwargs) -> "String8":
        return String8(self.state.format(*args, **kwargs))

    def __format__(self, format_spec: str) -> str:
        return format(self.state, format_spec)

    # UAF methods
    def serialize(self, am: "ArchiveMemory") -> "String8":
        size = uint32(len(self))
        size = am.serialize(size)

        content = am.serialize_block8(self.encode(), size).decode("utf-8", errors="strict")
        if am.is_reading():
            self.state = content  # Update the current instance
        return String8(content)

    def get_serialize_size(self) -> uint32:
        return uint32(len(self) + 4)  # size and len of char*

    def __len__(self) -> uint32:
        return uint32(len(bytes(self)))

    def __bytes__(self) -> bytes:
        return self.encode()

    def encode(self, encoding: str = "utf-8", errors: str = "strict") -> bytes:
        return self.state.encode(encoding, errors)

    def __bool__(self) -> bool:
        if self.lower() == "false":
            return False
        if self.lower() == "true":
            return True
        return True

    def is_integer(self) -> bool:
        try:
            int(self)
            return True
        except ValueError:
            return False

    def is_hexa_string(self) -> bool:
        try:
            int(self, 16)
            return True
        except ValueError:
            return False

    @staticmethod
    def encode_base64(_data: str) -> "String8":
        return String8(base64.b64encode(_data.encode()).decode())

    @staticmethod
    def decode_base64(_data: str) -> "String8":
        return String8(base64.b64decode(_data.encode()).decode())

    # Ensure compatibility with str
    def __instancecheck__(self, instance: object) -> bool:
        return isinstance(instance, str)

    def __subclasscheck__(self, subclass: type) -> bool:
        return issubclass(subclass, str)
