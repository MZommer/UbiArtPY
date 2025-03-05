from functools import singledispatchmethod
from typing import Callable
from typing import TypeVar, Generic, Iterable, Optional, Any

from .UAFCollection import UAFCollection

T = TypeVar('T')


class UAFList(UAFCollection[T], Generic[T]):
    @singledispatchmethod
    def __init__(self, values: Iterable[T]):
        super().__init__()
        if isinstance(values, UAFCollection):
            self.SerializableElements = values.SerializableElements
            self.element_type = values.element_type
        else:
            for value in values:
                self.add(value)

    @__init__.register
    def _(self):
        raise AttributeError("UAFList must be initialized with a type or a list of values")

    @__init__.register
    def _(self, element_type: type):
        super().__init__()
        self.element_type = element_type

    def __str__(self) -> str:
        return f'{self.count} {self.element_type}{"s" if self.count > 1 else ""}'

    def __getitem__(self, index):
        if isinstance(index, int):
            return self.SerializableElements[index]
        else:
            raise TypeError("Index must be an integer")

    def __setitem__(self, index, value):
        if isinstance(index, int):
            if isinstance(value, self.element_type):
                self.SerializableElements[index] = value
            else:
                raise TypeError(f"Value must be of type {self.element_type.__name__}")
        else:
            raise TypeError("Index must be an integer")

    def pop(self, index: int = -1):
        if isinstance(index, int):
            return self.SerializableElements.pop(index)
        else:
            raise TypeError("Index must be an integer")

    def remove(self, value):
        self.SerializableElements.remove(value)

    def append(self, value: T):
        if not isinstance(value, self.element_type):
            raise TypeError(f"Value must be of type {self.element_type.__name__}")
        self.add(value)

    def insert(self, index: int, value: T):
        if not isinstance(value, self.element_type):
            raise TypeError(f"Value must be of type {self.element_type.__name__}")
        if not isinstance(index, int):
            raise TypeError("Index must be an integer")
        self.SerializableElements.insert(index, value)

    def extend(self, values: Iterable[T]):
        for value in values:
            if not isinstance(value, self.element_type):
                raise TypeError(f"Value must be of type {self.element_type.__name__}")
            self.add(value)

    def reverse(self):
        self.SerializableElements.reverse()

    def sort(self, reverse: bool = False, key: Optional[Callable[[T], Any]] = None):
        self.SerializableElements.sort(reverse=reverse, key=key)
