from dataclasses import dataclass
from functools import singledispatchmethod
from .UAFCollection import UAFCollection
from typing import TypeVar, Generic

KT = TypeVar('KT')
VT = TypeVar('VT')
@dataclass
class SerializableKeyValuePair(Generic[KT, VT]):
    Key: any
    Value: any
    
    @property
    def KEY(self) -> any:
        return self.Key
    
    @property
    def VAL(self) -> any:
        return self.Value

class UAFDictionary(UAFCollection, Generic[KT, VT]):
    ElementType: type = SerializableKeyValuePair
    KType: type
    VType: type
    
    @singledispatchmethod
    def __init__(self) -> None:
        pass
    
    @__init__.register
    def _(self, KType: type, VType: type) -> None:
        super().__init__()
        self.KType = KType
        self.VType = VType
    
    @__init__.register
    def _(self, obj) -> None: # UAFDictionary
        super().__init__()
        self.KType = obj.KType
        self.VType = obj.VType
        self.SerializableElements = obj.SerializableElements.copy()
    
    @__init__.register
    def _(self, values: dict, KType: KT, VType: VT) -> None:
        super().__init__()
        self.KType = KType
        self.VType = VType
        for key, value in values.items():
            self.Add(key, value)
    
    def Set(self, key: KT, value: VT) -> None:
        self[key] = value

    def __setitem__(self, key: KT, value: VT) -> None:
        if not isinstance(key, self.KType):
            raise TypeError("Key must be an " + self.KType.__name__)
        if not isinstance(value, self.VType):
            raise TypeError("Value must be an " + self.VType.__name__)
        
        for pair in self:
            if pair.Key == key:
                pair.Value = value
                return
        raise KeyError(key)
    
    def Get(self, key: KT) -> VT:
        return self[key]
    
    def __getitem__(self, key: KT) -> VT:
        if isinstance(key, self.KType):
            for pair in self:
                if pair.Key == key:
                    return pair.Value
        else:
            raise TypeError("Key must be an " + self.KType.__name__)
    
    @singledispatchmethod
    def Add(self, *args):
        if len(args) == 1:
            pair: SerializableKeyValuePair = args[0]
            if isinstance(pair, SerializableKeyValuePair):
                if not isinstance(pair.Key, self.KType):
                    raise TypeError("Key must be an " + self.KType.__name__)
                if not isinstance(pair.Value, self.VType):
                    raise TypeError("Value must be an " + self.VType.__name__)
                self.SerializableElements.append(pair)
            else:
                raise TypeError("Value must be of type SerializableKeyValuePair")
        elif len(args) == 2:
            key, value = args
            self.Add(SerializableKeyValuePair(key, value))
        else:
            raise ValueError(f'Expected two arguments for key and value, but got {args}.')
        
    def Remove(self, key: KT) -> VT:
        for idx, pair in enumerate(self):
            if pair.Key == key:
                return self.SerializableElements.pop(idx)
    
    def ToDict(self) -> dict:
        ret: dict = {}
        
        for pair in self:
            ret[pair.Key] = pair.Value
            
        return ret
    
    def items(self):
        pass  # TODO: do iter
    def __str__(self):
        return str(self.ToDict())

                