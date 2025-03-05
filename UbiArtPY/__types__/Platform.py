from enum import IntEnum
from typing import Tuple, Iterable, Optional

from .JdVersion import (
    Jd2014, Jd2015, Jd2016, Jd2017, Jd2018,
    Jd2019, Jd2020, Jd2021, Jd2022, JdUnlimited,
    JdIgnored, JdVersion
)
from .String8 import String8
from .StringID import StringID
from .__base__ import uint32


class PlatformId(IntEnum):
    PC = uint32(0)
    X360 = uint32(1)
    PS3 = uint32(2)
    ORBIS = uint32(3)
    CTR = uint32(4)  # Unsupported / unused (Nintendo 3DS)
    WII = uint32(5)
    EMUWII = uint32(6)  # Unsupported / unused (WII emulation on PC)
    VITA = uint32(7)  # Unsupported / unused (PlayStation Vita)
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


LITTLE_ENDIAN_PLATFORMS = PlatformId.PC, PlatformId.X360, PlatformId.ORBIS, PlatformId.EMUWII, PlatformId.NX, PlatformId.SCARLETT, PlatformId.PROSPERO, PlatformId.BLAZEPOSE


class Platform:
    id: PlatformId
    name: String8
    available_versions: Tuple[JdVersion]

    def __init__(self, platform_id=None, available: Optional[Iterable[JdVersion]] = None):
        if isinstance(platform_id, PlatformId):
            self.id = platform_id
        elif isinstance(platform_id, int):
            try:
                self.id = PlatformId(platform_id)
            except ValueError:
                self.id = PlatformId.INVALID
        elif isinstance(platform_id, str):
            self.id = PlatformId.UNDEFINED
            for platformId in PlatformId:
                if platformId.name.lower() == platform_id.lower():
                    self.id = platformId
                    break
        else:
            self.id = PlatformId.UNDEFINED
        self.available_versions = tuple(available if available else ())

    def is_little_endian(self):
        return self.id in LITTLE_ENDIAN_PLATFORMS

    @property
    def name(self) -> String8:
        return String8(self.id.name)

    def to_string_id(self) -> StringID:
        return StringID(self.name)

    def __int__(self) -> uint32:
        return uint32(self.id)

    def __str__(self) -> String8:
        return self.name

    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, Platform):
            return self.id == __value.id
        elif isinstance(__value, PlatformId):
            return self.id == __value
        elif isinstance(__value, str):
            return self.name == __value
        return False


PC = Platform(PlatformId.PC, (Jd2017,))
X360 = Platform(PlatformId.X360, (Jd2014, Jd2015, Jd2016, Jd2017, Jd2018, Jd2019))
PS3 = Platform(PlatformId.PS3, (Jd2014, Jd2015, Jd2016, Jd2017, Jd2018))
ORBIS = Platform(PlatformId.ORBIS,
                 (Jd2014, Jd2015, Jd2016, Jd2017, Jd2018, Jd2019, Jd2020, Jd2021, Jd2022, JdUnlimited))
CTR = Platform(PlatformId.CTR, (JdIgnored,))
WII = Platform(PlatformId.WII, (Jd2014, Jd2015, Jd2016, Jd2017, Jd2018, Jd2019, Jd2020))
EMUWII = Platform(PlatformId.EMUWII, (JdIgnored,))
VITA = Platform(PlatformId.VITA, (JdIgnored,))
WIIU = Platform(PlatformId.WIIU, (Jd2014, Jd2015, Jd2016, Jd2017, Jd2018, Jd2019))
IPAD = Platform(PlatformId.IPAD, (JdIgnored,))
DURANGO = Platform(PlatformId.DURANGO,
                   (Jd2014, Jd2015, Jd2016, Jd2017, Jd2018, Jd2019, Jd2020, Jd2021, Jd2022, JdUnlimited))
NX = Platform(PlatformId.NX, (Jd2017, Jd2018, Jd2019, Jd2020, Jd2021, Jd2022))
GGP = Platform(PlatformId.GGP, (Jd2020,))
PROSPERO = Platform(PlatformId.PROSPERO, (Jd2021, Jd2022))
SCARLETT = Platform(PlatformId.SCARLETT, (Jd2021, Jd2022))
POSENET = Platform(PlatformId.POSENET, (JdIgnored,))
BLAZEPOSE = Platform(PlatformId.BLAZEPOSE, (JdIgnored,))
INVALID = Platform(PlatformId.INVALID, (JdIgnored,))

PLATFORMS = PC, X360, PS3, ORBIS, CTR, WII, EMUWII, VITA, WIIU, IPAD, DURANGO, NX, GGP, PROSPERO, SCARLETT, POSENET, BLAZEPOSE, INVALID


def get_platform_from_name(name: str) -> Platform:
    for platform in PLATFORMS:
        if platform.name == name:
            return platform
    return INVALID


def get_platform_from_id(platform_id: uint32) -> Platform:
    for platform in PLATFORMS:
        if platform.id == platform_id:
            return platform
    return INVALID
