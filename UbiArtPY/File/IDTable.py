from typing import Iterator

from ..Core import ArchiveMemory
from ..__types__ import StringID, Path, uint32, int32


class IDTable:
    def __init__(self):
        self._data = dict[StringID, int32]()

    def generate(self, dest_path: Path) -> bool:
        retval: bool = False

        try:
            with open(dest_path, 'wb') as f:
                am = ArchiveMemory()
                self.serialize(am)
                retval = bool(f.write(am.get_data()))
        except:
            pass

        return retval

    def load(self, src_path: Path) -> bool:
        retval: bool = False

        try:
            with ArchiveMemory.read_from_path(src_path) as am:
                retval = self.serialize(am)
        except:
            pass

        return retval

    def serialize(self, am: ArchiveMemory) -> bool:
        size = uint32(len(self))
        am.serialize(size)

        for file_id, file_idx in self.items() or ((StringID(i), int32(i)) for i in range(size)):
            file_id.serialize(am)
            file_idx = am.serialize(file_idx)
            if am.is_reading():
                self[file_id] = file_idx

        return True

    def insert_file(self, path: Path) -> None:
        if not isinstance(path, Path):
            path = Path(path)
        string_id = path.get_string_id()
        if string_id.is_valid():
            self[string_id] = int32(len(self))

    def __getitem__(self, key: StringID) -> int32:
        return self._data[key]

    def __setitem__(self, key: StringID, value: int32) -> None:
        if not isinstance(key, StringID):
            raise TypeError("Key must be StringID")
        if not isinstance(value, int32):
            raise TypeError("Value must be int32")
        self._data[key] = value

    def __len__(self) -> int:
        return len(self._data)

    def __iter__(self) -> Iterator[StringID]:
        return iter(self._data)

    def items(self):
        return self._data.items()

    def keys(self):
        return self._data.keys()

    def values(self):
        return self._data.values()

    def clear(self) -> None:
        self._data.clear()

    def get(self, key: StringID, default=None) -> int32:
        return self._data.get(key, default)

    def contains(self, key: StringID) -> bool:
        return key in self._data
