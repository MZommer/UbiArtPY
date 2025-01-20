# from ..Core import ArchiveMemory
from .__base__ import uint32
import base64

class String8(str):
    def serialize(self, am: "ArchiveMemory") -> None:
        size = uint32(len(self))
        size = am.serialize(size)
        
        content = am.serializeBlock8(self.encode(), size).decode("utf-8", errors="strict")
        if am.isReading():
            super(content)
    
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