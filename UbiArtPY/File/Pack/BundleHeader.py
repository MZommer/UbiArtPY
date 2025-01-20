from ...__types__ import uint32, Platform, Platforms, StringID
from ...Core import ArchiveMemory, Versioning, SerializableClass

PACK_MAGICNUMBER: uint32 = uint32(0x50EC12BA)

@SerializableClass
class BundleHeader:
    MagicNumber: uint32
    Version: uint32
    PlatformSupported: uint32
    FilesStart: uint32
    FilesCount: uint32
    Compressed: bool
    BinaryScene: bool
    BinaryLogic: bool
    DataSignature: uint32 # data version 0x00
    EngineSignature: uint32
    EngineVersion: uint32
    # File header count u32
    # Platform: Platform

    def __init__(self, platform: Platform, binary: bool = False, data_version: uint32 = uint32()) -> None:
        self.MagicNumber = uint32(PACK_MAGICNUMBER)
        self.Version = uint32(Versioning.Bundle)
        self.Platform = platform
        self.PlatformSupported = uint32(platform.Id)
        self.FilesStart = uint32(0)
        self.FilesCount = uint32(0)
        self.Compressed = False
        self.BinaryScene = binary
        self.BinaryLogic = binary
        self.DataSignature = uint32(data_version)
        self.EngineSignature = uint32(Versioning.EngineSignature)
        self.EngineVersion = uint32(Versioning.Engine) # TODO: make enviroment funcs
    
    def serialize(self, am: ArchiveMemory) -> None:
        self.MagicNumber = am.serialize(self.MagicNumber)
        assert self.MagicNumber == PACK_MAGICNUMBER, "Invalid magic! Not an IPK file."
        self.Version = am.serialize(self.Version)
        # assert self.Version == Versioning.Bundle, "Invalid bundle version! Make sure the enviroment is properly set."
        self.PlatformSupported = am.serialize(self.PlatformSupported)
        if am.isReading():
            self.Platform = Platform(self.PlatformSupported)
            assert self.Platform != Platforms.INVALID, "Invalid platform!"
        self.FilesStart = am.serialize(self.FilesStart)
        self.FilesCount = am.serialize(self.FilesCount)
        self.Compressed = am.serialize(uint32(self.Compressed))
        self.BinaryScene = am.serialize(uint32(self.BinaryScene))
        self.BinaryLogic = am.serialize(uint32(self.BinaryLogic))
        self.DataSignature = am.serialize(self.DataSignature)
        self.EngineSignature = am.serialize(self.EngineSignature)
        self.EngineVersion = am.serialize(self.EngineVersion)
    
    def compute_size(self) -> uint32:
        return uint32(44) # uint32 + uint32 + uint32 + uint32 + uint32 + uint32 + uint32 + uint32 + uint32 + uint32 + uint32