from typing import TypeVar, Generic, Iterable

T = TypeVar('T')

class UAFCollection(Generic[T]):
    ElementType: type
    SerializableElements: list[T]
    
    def __init__(self) -> None:
        self.SerializableElements = []
    
    def Clear(self):
        self.SerializableElements.clear()

    def Add(self, value):
        self.SerializableElements.append(value)
    
    @property
    def Count(self) -> int:
        return len(self)
    
    def __iter__(self) -> Iterable:
        return iter(self.SerializableElements)
    
    def __len__(self) -> int:
        return len(self.SerializableElements)


    
    