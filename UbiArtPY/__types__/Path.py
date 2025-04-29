from __future__ import annotations  # Enable forward references

from os import PathLike
from pathlib import Path as PathlibPath
from typing import Union

from .String8 import String8
from .StringID import StringID
from .__base__ import uint32

# from ..Core.SerializableClass import ArchiveMemory

PATH_C_BUFFER_SIZE: uint32 = uint32(256)
MaxBasenameLength: uint32 = uint32(64 + 1)  # Size, in characters, of the basename. Includes the null character.

PathType = Union[PathLike, str, String8, 'Path']


class Path(PathLike):
    """A class representing a filesystem path with additional functionality for serialization and manipulation."""

    _path: PathlibPath
    _flags: uint32

    @classmethod
    def empty_path(cls) -> 'Path':
        """
        Returns an empty Path object.
        """
        return cls(String8())

    def __init__(self, *args: PathType):
        """
        Initializes a Path object.

        Args:
            *args: Components of the path as String8 or str objects.
        """
        self._path = PathlibPath(*(str(arg) for arg in args))
        self._flags = uint32(0)  # Flags are not implemented yet

    def __repr__(self) -> str:
        """Returns a string representation of the Path object."""
        return f"Path({str(self)})"

    def __str__(self) -> str:
        """Returns the path as a string."""
        return self._path.as_posix() if self._path else ""

    def __fspath__(self) -> str:
        """Returns the path as a string for use with the os.PathLike protocol."""
        return str(self)

    def __hash__(self) -> int:
        """Returns the hash of the path based on its StringID."""
        return int(self.get_string_id().get_hash_code())

    def __eq__(self, other: Union['Path', str, StringID]) -> bool:
        """
        Checks if this Path is equal to another Path, string, or StringID.

        Args:
            other: The object to compare with.
        """
        if isinstance(other, Path):
            return str(self) == str(other)
        elif isinstance(other, str):
            return str(self) == other
        elif isinstance(other, StringID):
            return self.get_string_id() == other
        return False

    def __ne__(self, other: Union['Path', str, StringID]) -> bool:
        """
        Checks if this Path is not equal to another Path, string, or StringID.

        Args:
            other: The object to compare with.

        Returns:
            bool: True if the objects are not equal, False otherwise.
        """
        return not self.__eq__(other)

    def __lt__(self, other: Union['Path', str]) -> bool:
        """
        Checks if this Path is less than another Path or string.

        Args:
            other: The object to compare with.

        Returns:
            bool: True if this Path is less than the other, False otherwise.
        """
        return str(self) < str(other)

    def __gt__(self, other: Union['Path', str]) -> bool:
        """
        Checks if this Path is greater than another Path or string.

        Args:
            other: The object to compare with.

        Returns:
            bool: True if this Path is greater than the other, False otherwise.
        """
        return str(self) > str(other)

    def __le__(self, other: Union['Path', str]) -> bool:
        """
        Checks if this Path is less than or equal to another Path or string.

        Args:
            other: The object to compare with.

        Returns:
            bool: True if this Path is less than or equal to the other, False otherwise.
        """
        return str(self) <= str(other)

    def __ge__(self, other: Union['Path', str]) -> bool:
        """
        Checks if this Path is greater than or equal to another Path or string.

        Args:
            other: The object to compare with.

        Returns:
            bool: True if this Path is greater than or equal to the other, False otherwise.
        """
        return str(self) >= str(other)

    def __len__(self) -> int:
        """
        Returns the length of the path as a string.

        Returns:
            int: The length of the path.
        """
        return len(str(self))

    def serialize(self, _archive: 'ArchiveMemory', legacy: bool = False) -> bool:
        """
        Serializes the Path object into an ArchiveMemory object.

        Args:
            _archive: The ArchiveMemory object to serialize into.
            legacy: If True, uses the legacy serialization format.

        Returns:
            bool: True if serialization was successful, False otherwise.
        """
        from ..Core.Versioning import Versioning  # avoid circular import
        try:
            legacy = Versioning.Engine <= 109470 or legacy  # JD5 EngineVer (legacy path) TODO: take from Versioning
            basename = self.get_basename()
            assert (
                len(basename) < MaxBasenameLength,
                f"Path.serialize basename length exceeds MaxBasenameLength ({MaxBasenameLength})"
            )

            if not legacy:
                basename = basename.serialize(_archive)

            directory = self.get_directory()
            directory = directory.serialize(_archive)

            if legacy:
                basename = basename.serialize(_archive)

            if _archive.is_reading():
                assert (
                    len(directory) < PATH_C_BUFFER_SIZE,
                    f"Path.serialize directory length is bigger than {PATH_C_BUFFER_SIZE}"
                )
                self._path = PathlibPath(directory) / basename

            _id = self.get_string_id()
            _id.serialize(_archive)
            if _archive.is_reading() and _archive.is_strict():
                assert _id == self.get_string_id(), "Path.serialize StringID mismatch"

            self._flags = _archive.serialize(self._flags)
            return True
        except Exception as e:
            raise RuntimeError(f"Failed to serialize Path: {e}")

    def get_serialize_size(self) -> uint32:
        """Calculates the size of the serialized Path object."""
        directory = self.get_directory()
        basename = self.get_basename()
        len_directory = len(directory)
        len_basename = len(basename)
        return uint32(
            4  # directory length
            + len_directory  # directory
            + 4  # basename length
            + len_basename  # basename
            + 4  # string ID
            + 4  # flags
        )

    def get_string_id(self) -> StringID:
        """Returns the StringID representation of the path."""
        return StringID(String8(self))

    def get_basename(self) -> String8:
        """
        Returns the basename of the path.

        Returns:
            String8: The basename of the path.
        """
        return String8(self._path.name)

    def get_directory(self) -> String8:
        """
        Returns the directory of the path.

        Returns:
            String8: The directory of the path.
        """
        return String8(self._path.parent.as_posix() + "/")

    def set_directory(self, directory: String8):
        """
        Sets the directory of the path.

        Args:
            directory: The new directory as a String8 object.
        """
        self._path = PathlibPath(directory) / self._path.name

    def is_inside_directory(self, directory: String8) -> bool:
        """
        Checks if the path is inside the specified directory.

        Args:
            directory: The directory to check against.

        Returns:
            bool: True if the path is inside the directory, False otherwise.
        """
        directory_path = PathlibPath(directory)
        return directory_path in self._path.parents

    def get_depth(self) -> uint32:
        """
        Returns the depth of the path.

        Returns:
            uint32: The depth of the path.
        """
        return uint32(len(self._path.parts))

    def get_directory_at_depth(self, depth: uint32) -> String8:
        """
        Returns the directory component at the specified depth.

        Args:
            depth: The depth of the directory component to retrieve.

        Returns:
            String8: The directory component at the specified depth.
        """
        if 0 <= depth < len(self._path.parts):
            return String8(self._path.parts[depth])
        return String8()

    def get_sub_directory_at_depth(self, depth: uint32) -> String8:
        """
        Returns the subdirectory up to the specified depth.

        Args:
            depth: The depth of the subdirectory to retrieve.

        Returns:
            String8: The subdirectory up to the specified depth.
        """
        if depth < len(self._path.parts):
            return String8("/".join(self._path.parts[:depth]))
        return String8()

    def get_basename_without_extension(self) -> String8:
        """
        Returns the basename of the path without its extension.

        Returns:
            String8: The basename without the extension.
        """
        return String8(self._path.stem)

    def get_extension(self) -> String8:
        """
        Returns the extension of the path.

        Returns:
            String8: The extension of the path.
        """
        return String8(self._path.suffix)

    def change_directory(self, new_directory: String8):
        """
        Changes the directory of the path.

        Args:
            new_directory: The new directory as a String8 object.
        """
        self._path = PathlibPath(new_directory) / self._path.name

    def copy_and_change_directory(self, new_directory: String8) -> 'Path':
        """
        Returns a new Path object with the directory changed.

        Args:
            new_directory: The new directory as a String8 object.

        Returns:
            Path: A new Path object with the updated directory.
        """
        return Path(String8(PathlibPath(new_directory) / self._path.name))

    def change_basename(self, basename: String8):
        """
        Changes the basename of the path.

        Args:
            basename: The new basename as a String8 object.
        """
        self._path = self._path.with_name(basename)

    def copy_and_change_basename(self, new_basename: String8) -> 'Path':
        """
        Returns a new Path object with the basename changed.

        Args:
            new_basename: The new basename as a String8 object.

        Returns:
            Path: A new Path object with the updated basename.
        """
        return Path(String8(self._path.with_name(new_basename)))

    def change_extension(self, extension: String8):
        """
        Changes the extension of the path.

        Args:
            extension: The new extension as a String8 object.
        """
        self._path = self._path.with_suffix(extension)

    def copy_and_change_extension(self, new_extension: String8) -> 'Path':
        """
        Returns a new Path object with the extension changed.

        Args:
            new_extension: The new extension as a String8 object.

        Returns:
            Path: A new Path object with the updated extension.
        """
        return Path(String8(self._path.with_suffix(new_extension)))

    def copy_and_append(self, _suffix: Union[String8, 'Path']) -> 'Path':
        """
        Returns a new Path object with the suffix appended.

        Args:
            _suffix: The suffix to append as a String8 object.

        Returns:
            Path: A new Path object with the suffix appended.
        """
        return Path(String8(self._path / _suffix))

    def copy_and_append_path(self, _other_path: 'Path') -> 'Path':
        """
        Returns a new Path object with another Path appended.

        Args:
            _other_path: The Path to append.

        Returns:
            Path: A new Path object with the other Path appended.
        """
        return Path(String8(self._path / _other_path._path))

    def append(self, _suffix: String8):
        """
        Appends a suffix to the path.

        Args:
            _suffix: The suffix to append as a String8 object.
        """
        self._path = self._path / _suffix

    def append_path(self, _other_path: 'Path'):
        """
        Appends another Path to this Path.

        Args:
            _other_path: The Path to append.
        """
        self._path = self._path / _other_path._path

    def is_file(self):
        self._path.is_file()
