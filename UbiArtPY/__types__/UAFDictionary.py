from dataclasses import dataclass
from functools import singledispatchmethod
from typing import TypeVar, Generic, Iterator

from .UAFCollection import UAFCollection

KT = TypeVar('KT')
VT = TypeVar('VT')


@dataclass
class SerializableKeyValuePair(Generic[KT, VT]):
    key: any
    value: any

    @property
    def KEY(self) -> any:
        return self.key

    @property
    def VAL(self) -> any:
        return self.value


class UAFDictionary(UAFCollection[SerializableKeyValuePair[KT, VT]], Generic[KT, VT]):
    element_type: type = SerializableKeyValuePair
    KType: type
    VType: type

    @singledispatchmethod
    def __init__(self) -> None:
        super().__init__()

    @__init__.register
    def _(self, k_type: type, v_type: type) -> None:
        super().__init__()
        self.KType = k_type
        self.VType = v_type

    @__init__.register
    def _(self, obj) -> None:  # UAFDictionary
        super().__init__()
        self.KType = obj.KType
        self.VType = obj.VType
        self.SerializableElements = obj.SerializableElements.copy()

    @__init__.register
    def _(self, values: dict, k_type: KT, v_type: VT) -> None:
        super().__init__()
        self.KType = k_type
        self.VType = v_type
        for key, value in values.items():
            self.add(key, value)

    def set(self, key: KT, value: VT) -> None:
        if not isinstance(key, self.KType):
            raise TypeError("Key must be an " + self.KType.__name__)
        if not isinstance(value, self.VType):
            raise TypeError("Value must be an " + self.VType.__name__)

        for pair in self:
            if pair.key == key:
                pair.value = value
                return
        raise KeyError(key)

    def __setitem__(self, key: KT, value: VT) -> None:
        self.set(key, value)

    def get(self, key: KT) -> VT:
        return self[key]

    def __getitem__(self, key: KT) -> VT:
        if not isinstance(key, self.KType):
            raise TypeError(f"Key must be of type {self.KType.__name__}, got {type(key)}")
        for pair in self:
            if pair.key == key:
                return pair.value
        raise KeyError(f"Key '{key}' not found")

    def add(self, *args):
        if len(args) == 1:
            pair: SerializableKeyValuePair[KT, VT] = args[0]
            if not isinstance(pair, SerializableKeyValuePair):
                raise TypeError("Value must be of type SerializableKeyValuePair")
            if not isinstance(pair.key, self.KType):
                raise TypeError(f"Key must be of type {self.KType.__name__}")
            if not isinstance(pair.value, self.VType):
                raise TypeError(f"Value must be of type {self.VType.__name__}")
            self.SerializableElements.append(pair)
        elif len(args) == 2:
            key, value = args
            self.add(SerializableKeyValuePair(key, value))
        else:
            raise ValueError(f'Expected two arguments for key and value, but got {args}.')

    def remove(self, key: KT) -> VT:
        for idx, pair in enumerate(self):
            if pair.key == key:
                return self.SerializableElements.pop(idx).value
        raise KeyError(f"Key '{key}' not found")

    def to_dict(self) -> dict:
        ret: dict = {}

        for pair in self:
            ret[pair.key] = pair.value

        return ret

    def items(self) -> Iterator[SerializableKeyValuePair[KT, VT]]:
        return iter(self)

    def __str__(self) -> str:
        return str(self.to_dict())

    def __iter__(self) -> Iterator[SerializableKeyValuePair[KT, VT]]:
        return iter(self.SerializableElements)
