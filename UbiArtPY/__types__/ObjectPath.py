from dataclasses import dataclass, field

from .UAFList import UAFList


@dataclass
class Level:
    name: str = field(default='')
    parent: int = field(default='')


@dataclass
class ObjectPath:
    separator: str = '|'
    level_up: str = '..'

    levels: UAFList[Level] = field(default=UAFList(Level))
    id: str = field(default='')
    absolute: bool = field(default=False)

    def __init__(self, path: str = ''):
        ...  # TODO: do init
