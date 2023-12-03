from dataclasses import dataclass, field
from .UAFList import UAFList

@dataclass
class Level:
    Name: str = field(default='')
    Parent: int = field(default='')

@dataclass
class ObjectPath:
    Separator: str = '|'
    LevelUp: str = '..'
    
    Levels: UAFList[Level] = field(default=UAFList(Level))
    Id: str = field(default='')
    Absolute: bool = field(default=False)
    
    def __init__(self, path: str = ''):
        ...  # TODO: do init
