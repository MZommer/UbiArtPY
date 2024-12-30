from .__base__ import uint32, String8
from enum import IntEnum

class PlatformId(IntEnum):
    PC = uint32(0)
    X360 = uint32(1)
    PS3 = uint32(2)
    ORBIS = uint32(3)
    CTR = uint32(4)    # Unsupported / unused (Nintendo 3DS)
    WII = uint32(5)
    EMUWII = uint32(6) # Unsupported / unused (WII emulation on PC)
    VITA = uint32(7)   # Unsupported / unused (PlayStation Vita)
    WIIU = uint32(8)
    IPAD = uint32(9)
    DURANGO = uint32(10)
    NX = uint32(11)
    GGP = uint32(12)
    SCARLETT = uint32(13)
    PROSPERO = uint32(14)
    POSENET = uint32(15)
    BLAZEPOSE = uint32(16)
    UNDEFINED = uint32(17)
    INVALID = uint32(0xffffffff)

class Platform:
    Id: uint32
    Name: String8
    
    def __init__(self, id=None):
        if id is None:
            self.Id = PlatformId.UNDEFINED
        elif isinstance(id, PlatformId):
            self.Id = id
        elif isinstance(id, str):
            self.Id = PlatformId.UNDEFINED
            for platformId in PlatformId:
                if platformId.name.lower() == id.lower():
                    self.Id = platformId
                    break
    
    def is_little_endian(self):
        return self.Id in PlatformId.PC, PlatformId.X360, PlatformId.ORBIS, PlatformId.EMUWII, PlatformId.NX, PlatformId.SCARLETT, PlatformId.PROSPERO, PlatformId.BLAZEPOSE
    
    @property
    def Name(self):
        return self.Id.name

    def __int__(self) -> uint32:
        return uint32(self.Id)
    
    def __str__(self) -> String8:
        return String8(self.Name)
    
    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, Platform):
            return self.Id == __value.Id
        elif isinstance(__value, PlatformId):
            return self.Id == __value
        elif isinstance(__value, str):
            return self.Name == __value
        return False

PC = Platform(PlatformId.PC)
X360 = Platform(PlatformId.X360)
PS3 = Platform(PlatformId.PS3)
ORBIS = Platform(PlatformId.ORBIS)
CTR = Platform(PlatformId.CTR)
WII = Platform(PlatformId.WII)
EMUWII = Platform(PlatformId.EMUWII)
VITA = Platform(PlatformId.VITA)
WIIU = Platform(PlatformId.WIIU)
IPAD = Platform(PlatformId.IPAD)
DURANGO = Platform(PlatformId.DURANGO)
NX = Platform(PlatformId.NX)
GGP = Platform(PlatformId.GGP)
PROSPERO = Platform(PlatformId.PROSPERO)
SCARLETT = Platform(PlatformId.SCARLETT)
POSENET = Platform(PlatformId.POSENET)
BLAZEPOSE = Platform(PlatformId.BLAZEPOSE)
