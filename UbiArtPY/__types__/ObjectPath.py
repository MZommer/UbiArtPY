from dataclasses import dataclass, field

from .String8 import String8
from .UAFList import UAFList
from .__base__ import int32


@dataclass
class Level:
    name: String8 = field(default='')
    parent: int32 = field(default=0)


@dataclass
class ObjectPath:
    separator: String8 = String8('|')
    level_up: String8 = String8('..')

    levels: UAFList[Level] = field(default_factory=lambda: UAFList(Level))
    id: String8 = field(default=String8())
    absolute: bool = field(default=False)

    def __init__(self, path: str = ''):
        ...  # TODO: do init
