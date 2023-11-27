from enum import Enum

class PlatformId(Enum):
    PC = 1
    X360 = 2
    PS3 = 3
    ORBIS = 4
    CTR = 5
    WII = 6
    EMUWII = 7
    VITA = 8
    WIIU = 9
    IPAD = 10
    DURANGO = 11
    NX = 12
    GGP = 13
    SCARLETT = 14
    PROSPERO = 15
    POSENET = 16
    BLAZEPOSE = 17
    UNDEFINED = 18

class Platform:
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

    @property
    def Name(self):
        return self.Id.name

    def __str__(self):
        return self.Name
    
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
POSENET = Platform(PlatformId.POSENET)
BLAZEPOSE = Platform(PlatformId.BLAZEPOSE)
