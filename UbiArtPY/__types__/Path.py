from .__base__ import uint32, uint8, get_sizeof
from .String8 import String8
from .StringID import StringID
from ..Core import Versioning
# from ..Core import ArchiveMemory  # circular import
from pathlib import Path as PathlibPath
from os import PathLike

PATH_C_BUFFERSIZE: uint32 = uint32(256)
MaxBasenameLength: uint32 = uint32(64 + 1) # Size, in character, of the basename. Includes the 0 character.

class Path(PathLike):
    _path: PathlibPath
    _flags: uint32
    
    @property
    @staticmethod
    def EmptyPath():
        return Path(String8(""))
    
    def __init__(self, *args: String8):
        args = tuple(str(i) for i in args)
        self._path = PathlibPath(*args)
        self._flags = uint32(0) # NOT IMPLEMENTED
        # TODO: implement flagss

    def __repr__(self):
        return f"Path({str(self)})"

    def __str__(self):
        return self._path.as_posix() if self._path else ""
    
    def __fspath__(self):
        return str(self)
    
    def __hash__(self):
        return int(self.getStringID().GetHashCode())
    
    def __eq__(self, other):
        if isinstance(other, Path):
            return str(self) == str(other)
        elif isinstance(other, str):
            return str(self) == other
        elif isinstance(other, StringID):
            return self.getStringID() == other
        return False
    
    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __lt__(self, other):
        return str(self) < str(other)
    
    def __gt__(self, other):
        return str(self) > str(other)
    
    def __le__(self, other):
        return str(self) <= str(other)
    
    def __ge__(self, other):
        return str(self) >= str(other)
    
    def __len__(self):
        return len(str(self))
    
    def serialize(self, _archive: "ArchiveMemory", legacy: bool = False):
        """_summary_

        Args:
            _archive (ArchiveMemory): ArchiveMemory object
            legacy (bool, optional): First iteration of the engine (ENGINEVER) serializes this object differently. Defaults to False.
        """
        
        legacy = Versioning.Engine <= 109470 or legacy # JD5 EngineVer (legacy path)
        basename = self.getBasename()
        # Assert basename length
        assert len(basename) < MaxBasenameLength, f"Path.serialize basename length exceeds MaxBasenameLength ({MaxBasenameLength})"
        
        if not legacy:
            basename.serialize(_archive)
        
        directory = self.getDirectory()
        directory.serialize(_archive)
        
        if legacy:
            basename.serialize(_archive)

        if _archive.isReading():
            assert len(directory) < PATH_C_BUFFERSIZE, f"Path.serialize directory length is bigger than PATH_C_BUFFERSIZE ({PATH_C_BUFFERSIZE})"
            
            # Since we're using pathlib.Path instead of a directory entry system,
            # we'll store the directory directly
            self._path = PathlibPath(directory) / basename
        
        _id = self.getStringID()
        _id.serialize(_archive)
        if _archive.isReading() and _archive.isStrict():
            assert _id == self.getStringID(), "Path.serialize stringid mismatch"
        
        self._flags = _archive.serialize(self._flags)

    def getSerializeSize(self) -> uint32:
        directory = self.getDirectory()
        basename = self.getBasename()
        
        # Calculate lengths
        len_directory = len(directory)
        len_basename = len(basename)
        
        # Calculate total size
        return (
            get_sizeof(uint32)                    # directory length
            + len_directory * get_sizeof(uint8)   # directory
            + get_sizeof(uint32)                  # basename length
            + len_basename * get_sizeof(uint8)    # basename
            + get_sizeof(uint32)                  # string ID
            + get_sizeof(uint32)                  # flags
            )


    def getStringID(self) -> StringID:
        return StringID(str(self))
    
    def getBasename(self) -> String8:
        return String8(self._path.name)
    
    def getDirectory(self) -> String8:
        return String8(self._path.parent.as_posix())
    
    def setDirectory(self, directory: String8):
        self._path = PathlibPath(directory, self._path.name)

    def isInsideDirectory(self, directory: String8) -> bool:
        directory_path = PathlibPath(directory)
        return directory_path in self._path.parents

    def getDepth(self) -> uint32:
        return uint32(len(self._path.parts))

    def getDirectoryAtDepth(self, depth: uint32) -> String8:
        if 0 <= depth < len(self._path.parts):
            return String8(self._path.parts[depth])
        return String8("")

    def getSubDirectoryAtDepth(self, depth: uint32) -> String8:
        if depth < len(self._path.parts):
            return String8("/".join(self._path.parts[:depth]))
        return String8("")

    def getBasenameWithoutExtension(self) -> String8:
        return String8(self._path.stem)

    def getExtension(self) -> String8:
        return String8(self._path.suffix)

    def changeDirectory(self, new_directory: String8):
        self._path = PathlibPath(new_directory, self._path.name)

    def copyAndChangeDirectory(self, new_directory: String8) -> 'Path':
        return Path(String8(PathlibPath(new_directory, self._path.name)))

    def changeBasename(self, basename: String8):
        self._path = PathlibPath(self._path.parent / basename)

    def copyAndChangeBasename(self, new_basename: String8) -> 'Path':
        return Path(String8(PathlibPath(self._path.parent, new_basename)))

    def changeExtension(self, extension: String8):
        self._path = self._path.with_suffix(extension)

    def copyAndChangeExtension(self, new_extension: String8) -> 'Path':
        return Path(String8(self._path.with_suffix(new_extension)))

    def copyAndAppend(self, _suffix: String8) -> 'Path':
        return Path(self._path / String8(_suffix))

    def copyAndAppendPath(self, _other_path: 'Path') -> 'Path':
        return Path(String8(self._path / _other_path._path))

    def append(self, _suffix: String8):
        self._path = PathlibPath(self._path / String8(_suffix))

    def appendPath(self, _other_path: 'Path'):
        self._path = self._path / _other_path._path
