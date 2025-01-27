from ...__types__ import StringID, Path, String8, uint8, uint16
from dataclasses import dataclass

@dataclass(slots=True)
class FileLinkBundleId:
    m_id: uint16
    m_idActive: uint16

@dataclass(slots=True)
class FileLinkBundleIds:
    m_index: uint16
    m_unused: uint16

@dataclass(slots=True)
class FileLink:
    bundleId: FileLinkBundleId
    bundleIds: FileLinkBundleIds
    
    def __init__(self) -> None:
        self.bundleId = FileLinkBundleId()
        self.bundleIds = FileLinkBundleIds()

BundleSet = set[String8]
FileSet = dict[Path, BundleSet]
TOC8 = dict[String8, uint8]
BundleTOC = dict[uint8, String8]
BundleIds = list[uint8]
FileLinks = dict[StringID, FileLink]
