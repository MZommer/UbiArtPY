from typing import Callable
from .UAFCollection import UAFCollection
from typing import TypeVar, Generic, Iterable
from functools import singledispatchmethod

T = TypeVar('T')

class UAFList(UAFCollection, Generic[T]):
    
    @singledispatchmethod
    def __init__(self, values, t) -> None:
        super().__init__()
        if isinstance(values, UAFCollection): 
            self.SerializableElements = values.SerializableElements
            self.ElementType = values.ElementType
        else:
            for value in values:
                self.Add(value)
            self.ElementType = t or type(value) # expecting that all the list has the same type inside.
    
    
    @__init__.register
    def _(self) -> None:
        raise AttributeError("UAFList must be initialized with a type or a list of values")
    
    @__init__.register
    def _(self, T: type) -> None:
        super().__init__()
        self.ElementType = T
    
    
    def __str__(self) -> str:
        return f'{self.Count} {self.ElementType.__name__}{"s" if self.Count > 1 else ""}'
    
    def __getitem__(self, index):
        if isinstance(index, int):
            return self.SerializableElements[index]
        else:
            raise TypeError("Index must be an integer")

    def __setitem__(self, index, value):
        if isinstance(index, int):
            if isinstance(value, self.ElementType):
                self.SerializableElements[index] = value
            else:
                raise TypeError(f"Value must be of type {self.ElementType.__name__}")
        else:
            raise TypeError("Index must be an integer")
    
    def pop(self, index):
        if isinstance(index, int):
            return self.SerializableElements.pop(index)
        else:
            raise TypeError("Index must be an integer")
    
    def remove(self, value):
        self.SerializableElements.remove(value)
    
    def append(self, value):
        self.Add(value)
    
    def insert(self, index, value):
        if not isinstance(value, self.ElementType):
            raise TypeError(f"Value must be of type {self.ElementType.__name__}")
        
        if isinstance(index, int):
            self.SerializableElements.insert(index, value)
        else:
            raise TypeError("Index must be an integer")
    
    def extend(self, values: Iterable):
        for value in values:
            if isinstance(value, self.ElementType):
                self.Add(value)
            else:
                raise TypeError("Value must be of type {self.ElementType.__name__}")
    
    def reverse(self):
        self.SerializableElements.reverse()
    
    def sort(self, reverse: bool = False, key: Callable = None):
        self.SerializableElements.sort(reverse=reverse, key=key)

    def pop(self, index: int = -1):
        return self.SerializableElements.pop(index)
