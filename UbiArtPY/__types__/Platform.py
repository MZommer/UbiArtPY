from .__base__ import uint32
from .String8 import String8
from .StringID import StringID
from .JdVersion import *
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
    AvailableVersions: tuple[JdVersion]
    
    def __init__(self, id=None, available: tuple[JdVersion] = None):
        if isinstance(id, PlatformId):
            self.Id = id
        elif isinstance(id, int):
            try:
                self.Id = PlatformId(id)
            except ValueError:
                self.Id = PlatformId.INVALID
        elif isinstance(id, str):
            self.Id = PlatformId.UNDEFINED
            for platformId in PlatformId:
                if platformId.name.lower() == id.lower():
                    self.Id = platformId
                    break
        else:
            self.Id = PlatformId.UNDEFINED
        if available:
            self.AvailableVersions = available
        else:
            self.AvailableVersions = tuple()
    
    def is_little_endian(self):
        return self.Id in PlatformId.PC, PlatformId.X360, PlatformId.ORBIS, PlatformId.EMUWII, PlatformId.NX, PlatformId.SCARLETT, PlatformId.PROSPERO, PlatformId.BLAZEPOSE
    
    @property
    def Name(self):
        return String8(self.Id.name)

    def ToStringID(self):
        return StringID(self.Name)
    
    def __int__(self) -> uint32:
        return uint32(self.Id)
    
    def __str__(self) -> String8:
        return self.Name
    
    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, Platform):
            return self.Id == __value.Id
        elif isinstance(__value, PlatformId):
            return self.Id == __value
        elif isinstance(__value, str):
            return self.Name == __value
        return False

PC = Platform(PlatformId.PC, (Jd2017,))
X360 = Platform(PlatformId.X360, (Jd2014, Jd2015, Jd2016, Jd2017, Jd2018, Jd2019))
PS3 = Platform(PlatformId.PS3, (Jd2014, Jd2015, Jd2016, Jd2017, Jd2018))
ORBIS = Platform(PlatformId.ORBIS, (Jd2014, Jd2015, Jd2016, Jd2017, Jd2018, Jd2019, Jd2020, Jd2021, Jd2022, JdUnlimited))
CTR = Platform(PlatformId.CTR, (JdIgnored,))
WII = Platform(PlatformId.WII, (Jd2014, Jd2015, Jd2016, Jd2017, Jd2018, Jd2019, Jd2020))
EMUWII = Platform(PlatformId.EMUWII, (JdIgnored,))
VITA = Platform(PlatformId.VITA, (JdIgnored,))
WIIU = Platform(PlatformId.WIIU, (Jd2014, Jd2015, Jd2016, Jd2017, Jd2018, Jd2019))
IPAD = Platform(PlatformId.IPAD, (JdIgnored,))
DURANGO = Platform(PlatformId.DURANGO, (Jd2014, Jd2015, Jd2016, Jd2017, Jd2018, Jd2019, Jd2020, Jd2021, Jd2022, JdUnlimited))
NX = Platform(PlatformId.NX, (Jd2017, Jd2018, Jd2019, Jd2020, Jd2021, Jd2022))
GGP = Platform(PlatformId.GGP, (Jd2020,))
PROSPERO = Platform(PlatformId.PROSPERO, (Jd2021, Jd2022))
SCARLETT = Platform(PlatformId.SCARLETT, (Jd2021, Jd2022))
POSENET = Platform(PlatformId.POSENET, (JdIgnored,))
BLAZEPOSE = Platform(PlatformId.BLAZEPOSE, (JdIgnored,))
INVALID = Platform(PlatformId.INVALID, (JdIgnored,))

PLATFORMS = PC, X360, PS3, ORBIS, CTR, WII, EMUWII, VITA, WIIU, IPAD, DURANGO, NX, GGP, PROSPERO, SCARLETT, POSENET, BLAZEPOSE, INVALID

def GetPlatformFromName(name: str):
    for platform in PLATFORMS:
        if platform.Name == name:
            return platform
    return INVALID

def GetPlatformFromId(id: int):
    for platform in PLATFORMS:
        if platform.Id == id:
            return platform
    return INVALID