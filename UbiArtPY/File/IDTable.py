from typing import Iterator, Optional

from ..Core.Archive import ArchiveMemory
from ..__types__ import StringID, Path, uint32, int32


class IDTable:
    """
    A class to manage a mapping of bundles. Named ID Table cause is a mapping of StringIDs.
    Supports serialization, deserialization, and file operations.
    """

    def __init__(self):
        self._data = dict[StringID, int32]()

    def generate(self, dest_path: Path) -> bool:
        """
        Serialize the IDTable and write it to a file.

        Args:
            dest_path (Path): The path to the destination file.

        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        try:
            with open(dest_path, 'wb') as f:
                am = ArchiveMemory()
                self.serialize(am)
                f.write(am.get_data())
                return True
        except (IOError, OSError) as e:
            print(f"Error writing to file {dest_path}: {e}")
            return False

    def load(self, src_path: Path) -> bool:
        """
        Load and deserialize the IDTable from a file.

        Args:
            src_path (Path): The path to the source file.

        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        try:
            with ArchiveMemory.read_from_path(src_path) as am:
                return self.serialize(am)
        except (IOError, OSError) as e:
            print(f"Error reading from file {src_path}: {e}")
            return False

    def serialize(self, am: ArchiveMemory) -> bool:
        """
        Serialize or deserialize the IDTable using an ArchiveMemory object.

        Args:
            am (ArchiveMemory): The ArchiveMemory object to use for serialization.

        Returns:
            bool: True if the operation was successful.
       """
        size = uint32(len(self))
        am.serialize(size)

        for file_id, file_idx in self.items() or ((StringID(i), int32(i)) for i in range(size)):
            file_id.serialize(am)
            file_idx = am.serialize(file_idx)
            if am.is_reading():
                self[file_id] = file_idx

        return True

    def insert_file(self, path: Path) -> None:
        """
        Insert a file path into the IDTable.

        Args:
            path (Path): The path to the file.
        """
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
        """Clear all entries in the IDTable."""
        self._data.clear()

    def get(self, key: StringID, default: Optional[int32] = None) -> int32:
        """
        Get the value associated with a key, or return a default value if the key is not found.

        Args:
            key (StringID): The key to look up.
            default (Optional[int32]): The default value to return if the key is not found.

        Returns:
            Optional[int32]: The value associated with the key, or the default value.
        """
        return self._data.get(key, default)

    def contains(self, key: StringID) -> bool:
        """
        Check if the IDTable contains a specific key.

        Args:
            key (StringID): The key to check.

        Returns:
            bool: True if the key is present, False otherwise.
        """
        return key in self._data
