from ...Core.Archive import ArchiveMemory
from ...Core.SerializableClass import serializable_class
from ...Core.Versioning import Versioning
from ...__types__ import uint32, Platform, Platforms

PACK_MAGIC_NUMBER = uint32(0x50EC12BA)
uint32(1357648570)


@serializable_class
class BundleHeader:
    magic_number: uint32
    version: uint32
    platform_supported: uint32
    files_start: uint32
    files_count: uint32
    compressed: bool
    binary_scene: bool
    binary_logic: bool
    data_signature: uint32  # data version 0x00
    engine_signature: uint32
    engine_version: uint32

    # File header count u32
    # Platform: Platform

    def __init__(self, platform: Platform, binary: bool = False, data_version: uint32 = uint32()) -> None:
        self.magic_number = uint32(PACK_MAGIC_NUMBER)
        self.version = uint32(Versioning.Bundle)
        self.platform = platform
        self.platform_supported = uint32(platform.id)
        self.files_start = uint32(0)
        self.files_count = uint32(0)
        self.compressed = False
        self.binary_scene = binary
        self.binary_logic = binary
        self.data_signature = uint32(data_version)
        self.engine_signature = uint32(Versioning.EngineSignature)
        self.engine_version = uint32(Versioning.Engine)  # TODO: make environment funcs

    def __repr__(self):
        return f"BundleHeader({self.version}, {self.platform}, {self.compressed}, {self.engine_signature}, {self.engine_version})"

    def serialize(self, am: ArchiveMemory) -> None:
        self.magic_number = am.serialize(self.magic_number)
        assert self.magic_number == PACK_MAGIC_NUMBER, "Invalid magic! Not an IPK file."
        self.version = am.serialize(self.version)
        # assert self.Version == Versioning.Bundle, "Invalid bundle version! Make sure the environment is properly set."
        self.platform_supported = am.serialize(self.platform_supported)
        if am.is_reading():
            self.platform = Platforms.get_platform_from_id(self.platform_supported)
            assert self.platform != Platforms.INVALID, "Invalid platform!"
        self.files_start = am.serialize(self.files_start)
        self.files_count = am.serialize(self.files_count)
        self.compressed = am.serialize(uint32(self.compressed))
        self.binary_scene = am.serialize(uint32(self.binary_scene))
        self.binary_logic = am.serialize(uint32(self.binary_logic))
        self.data_signature = am.serialize(self.data_signature)
        self.engine_signature = am.serialize(self.engine_signature)
        self.engine_version = am.serialize(self.engine_version)
        Versioning.Engine = self.engine_version
        Versioning.EngineSignature = self.engine_signature

    @staticmethod
    def compute_size() -> uint32:
        return uint32(44)
        # uint32 + uint32 + uint32 + uint32 + uint32 + uint32 + uint32 + uint32 + uint32 + uint32 + uint32
