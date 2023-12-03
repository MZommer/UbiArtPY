from .Angle import Angle
from .Color import Color
from .ColorInteger import ColorInteger
from .LocalisationId import LocalisationId
from .ObjectPath import ObjectPath
from .Path import Path
from .Platform import Platform
from .String8 import String8
from .StringID import StringID
from .URL import URL
from .Vec2d import Vec2d
from .Vec3d import Vec3d
from .Volume import Volume
from .__base__ import BaseTypes

class BasicTypeList:
    TypeList: tuple[type] =  (
        Angle,
        Color,
        ColorInteger,
        LocalisationId,
        ObjectPath,
        Path,
        Platform,
        String8,
        StringID,
        URL,
        Vec2d,
        Vec3d,
        Volume,
    )
    
    def IsBaseType(_type: type) -> bool:
        return _type in BasicTypeList.TypeList or _type in BaseTypes
