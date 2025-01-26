# from ..Core import ArchiveMemory
from .__base__ import uint32
import base64

class String8(str): # to keep compatibility
    state: str # current state
    def __init__(self, value):
        self.state = str(value)

    def __str__(self):
        return self.state

    def __repr__(self):
        return self.state

    def __len__(self):
        return len(self.state)

    def __getitem__(self, key):
        return self.state[key]

    def __contains__(self, item):
        return item in self.state

    def __add__(self, other):
        return String8(self.state + str(other))

    def __eq__(self, other):
        return self.state == str(other)

    # String methods
    def lower(self):
        return String8(self.state.lower())

    def upper(self):
        return String8(self.state.upper())

    def strip(self, chars=None):
        return String8(self.state.strip(chars))

    def split(self, sep=None, maxsplit=-1):
        return self.state.split(sep, maxsplit)

    def replace(self, old, new, count=-1):
        return String8(self.state.replace(old, new, count))

    def startswith(self, prefix):
        return self.state.startswith(prefix)

    def endswith(self, suffix):
        return self.state.endswith(suffix)

    def find(self, sub, start=0, end=None):
        return self.state.find(sub, start, end)

    def index(self, sub, start=0, end=None):
        return self.state.index(sub, start, end)

    def isalnum(self):
        return self.state.isalnum()

    def isalpha(self):
        return self.state.isalpha()

    def isdigit(self):
        return self.state.isdigit()

    def islower(self):
        return self.state.islower()

    def isupper(self):
        return self.state.isupper()

    def isspace(self):
        return self.state.isspace()

    def join(self, iterable):
        return String8(self.state.join(iterable))

    def serialize(self, new):
        self.state = str(new)

    # Format methods
    def format(self, *args, **kwargs):
        return String8(self.state.format(*args, **kwargs))

    def __format__(self, format_spec):
        return self.state.__format__(format_spec)
    
    # UAF methods
    def serialize(self, am: "ArchiveMemory") -> None:
        size = uint32(len(self))
        size = am.serialize(size)

        content = am.serializeBlock8(self.encode(), size).decode("utf-8", errors="strict")
        if am.isReading():
            self.state = content  # Update the current instance
        return String8(content)

    
    def getSerializeSize(self) -> uint32:
        return uint32(len(self) + 4) # size and len of char*
    
    def __len__(self) -> uint32:
        return uint32(len(bytes(self)))
    
    def __bytes__(self) -> bytes:
        return self.encode()
    
    def encode(self, encoding = "utf-8", errors = "strict"):
        return super().encode(encoding, errors)
    
    def __bool__(self) -> bool:
        if self.lower() == "false":
            return False
        if self.lower() == "true":
            return True
        return True
    
    def isInteger(self) -> bool:
        try:
            int(self)
            return True
        except ValueError:
            return False
    
    def isHexaString(self) -> bool:
        try:
            int(self, 16)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def encodeBase64(_data: str) -> str:
        return String8(base64.b64encode(_data.encode()).decode())
    
    @staticmethod
    def decodeBase64(_data: str) -> str:
        return String8(base64.b64decode(_data.encode()).decode())

