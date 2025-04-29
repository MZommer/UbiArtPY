import base64
from typing import Union, Any

from .__base__ import uint32


class String8(str):  # Inherits from str for compatibility
    def __new__(cls, value: Any = "") -> str:
        # Ensure we create a proper str instance first
        instance = super().__new__(cls, str(value))
        instance.state = str(value)
        return instance

    def __init__(self, value: Any = "") -> None:
        # Already handled in __new__
        pass

    def __repr__(self) -> str:
        # Directly use the underlying str's __repr__
        return f"String8({super().__repr__()})"

    # Rest of the methods remain the same...
    def __getitem__(self, key: Union[int, slice]) -> "String8":
        return String8(super().__getitem__(key))

    # UAF methods
    def serialize(self, am: "ArchiveMemory") -> "String8":
        size = uint32(len(self))
        size = am.serialize(size)

        content = am.serialize_block8(self.encode(), size).decode("utf-8", errors="strict")
        return String8(content)

    def get_serialize_size(self) -> uint32:
        return uint32(len(self) + 4)  # size and len of char*

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
