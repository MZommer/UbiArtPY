from dataclasses import dataclass

from ...Core.SerializableClass import serializable_class
from ...__types__ import StringID, Path, String8, uint8, uint16


@dataclass(slots=True)
@serializable_class
class FileLinkBundleId:
    id: uint16 = 0
    id_active: uint16 = 0


@dataclass(slots=True)
@serializable_class
class FileLinkBundleIds:
    index: uint16 = 0
    unused: uint16 = 0


@dataclass(slots=True)
class FileLink:
    bundle_id: FileLinkBundleId
    bundle_ids: FileLinkBundleIds

    def __init__(self) -> None:
        self.bundle_id = FileLinkBundleId()
        self.bundle_ids = FileLinkBundleIds()


BundleSet = set[String8]
FileSet = dict[Path, BundleSet]
TOC8 = dict[String8, uint8]
BundleTOC = dict[uint8, String8]
BundleIds = list[uint8]
FileLinks = dict[StringID, FileLink]
