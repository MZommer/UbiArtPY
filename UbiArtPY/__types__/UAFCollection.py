import abc
from typing import TypeVar, Generic, Iterable, Iterator, List

T = TypeVar('T')


class UAFCollection(Generic[T], Iterable[T], abc.ABC):
    element_type: type
    SerializableElements: List[T]

    def __init__(self):
        self.SerializableElements = []

    def clear(self):
        self.SerializableElements.clear()

    def add(self, value):
        if not self.element_type:
            self.element_type = type(value)
        if not isinstance(value, self.element_type):
            raise TypeError(f"Expected type {self.element_type}, got {type(value)}")
        self.SerializableElements.append(value)

    def remove(self, value: T) -> None:
        if not isinstance(value, self.element_type):
            raise TypeError(f"Expected type {self.element_type}, got {type(value)}")
        self.SerializableElements.remove(value)

    @property
    def count(self) -> int:
        return len(self)

    def __iter__(self) -> Iterator[T]:
        return iter(self.SerializableElements)

    def __len__(self) -> int:
        return len(self.SerializableElements)

    def __contains__(self, item: T) -> bool:
        return item in self.SerializableElements

    def __getitem__(self, index: int) -> T:
        return self.SerializableElements[index]

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.SerializableElements}, element_type={self.element_type},)"

    def __str__(self) -> str:
        return str(self.SerializableElements)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, UAFCollection):
            return NotImplemented
        return self.SerializableElements == other.SerializableElements

    def __ne__(self, other: object) -> bool:
        if not isinstance(other, UAFCollection):
            return NotImplemented
        return self.SerializableElements != other.SerializableElements
