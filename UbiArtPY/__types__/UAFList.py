from typing import Callable
from typing import TypeVar, Generic, Iterable, Optional, Any

from .UAFCollection import UAFCollection

T = TypeVar('T')


class UAFList(UAFCollection[T], Generic[T]):
    def __init__(self, *args):
        """
       Initialize a UAFList instance.

       The constructor supports the following initialization patterns:
       1. Initialize with an iterable of values:
          Example: UAFList([1, 2, 3])
       2. Initialize with an element type:
          Example: UAFList(int)
       3. Initialize with a UAFCollection:
          Example: UAFList(another_uaf_collection)

       Args:
           *args: Variable-length argument list. Valid inputs are:
               - A single iterable of values (Iterable[T]).
               - A single type (type) to set the element_type.
               - A single UAFCollection to copy elements and element_type.

       Raises:
           AttributeError: If no arguments are provided.
           TypeError: If the arguments are invalid or unsupported.
       """
        super().__init__()
        if len(args) == 1:
            # Case 1: Single argument (Iterable[T] or UAFCollection)
            values = args[0]
            if isinstance(values, type):
                # Case 2: Single argument (element_type as a type)
                self.element_type = args[0]
            elif isinstance(values, UAFCollection):
                self.SerializableElements = values.SerializableElements
                self.element_type = values.element_type
            else:
                for value in values:
                    self.add(value)
        elif len(args) == 0:
            # Case 3: No arguments (raise error)
            raise AttributeError("UAFList must be initialized with a type or a list of values")
        else:
            # Case 4: Invalid arguments
            raise TypeError("Invalid arguments for UAFList initialization")

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
