from typing import List

from .FatConst import FILE_SIGNATURE, FILE_VERSION, IndexToBundleIdsArray_Mask
from .__types__ import BundleTOC, BundleIds, FileLink, FileLinks
from ...Core import ArchiveMemory
from ...__types__ import StringID, Path, String8, uint8, uint32


class BundleIDsLoader:
    file_link: FileLink

    def __init__(self, bundle_ids: BundleIds, am: ArchiveMemory, offset_pos: uint32) -> None:
        self.file_link = FileLink()
        bundles = uint32()
        bundles = am.serialize(bundles)

        self.file_link.bundle_id.id_active = bundles == 1

        if self.file_link.bundle_id.id_active:
            bundle_id = uint8()
            bundle_id = am.serialize(bundle_id)
            self.file_link.bundle_id.id = bundle_id + offset_pos
        else:
            idx_in_bundles_array = uint32(len(bundle_ids))
            assert (
                idx_in_bundles_array <= IndexToBundleIdsArray_Mask,
                "Value overflow! Please check FileLink structure!"
            )
            self.file_link.bundle_ids.index = idx_in_bundles_array & IndexToBundleIdsArray_Mask
            bundle_ids.append(bundles)
            for _ in range(bundles):
                bundle_id = uint8()
                bundle_id = am.serialize(bundle_id)
                bundle_ids.append(uint8(bundle_id + offset_pos))

    def get_link(self) -> FileLink:
        return self.file_link


class BundleIDsExtractor:
    file_link: FileLink
    bundle_ids: BundleIds

    def __init__(self, file_link: FileLink, bundle_ids: BundleIds) -> None:
        self.file_link = file_link
        self.bundle_ids = bundle_ids

    def get_size(self) -> int:
        return len(self.bundle_ids)

    def get_id(self, index: int) -> List[uint8]:
        return self.bundle_ids[uint32(index)]


class FatBase:
    bundle_toc: BundleTOC
    files: FileLinks
    bundleIds: BundleIds
    bundle_root: Path
    id: StringID
    engine_signature: uint32

    def __init__(self) -> None:
        self.bundle_toc: BundleTOC = {}
        self.files: FileLinks = {}
        self.bundleIds: BundleIds = []
        self.bundle_root = Path()
        self.id = StringID()
        self.engine_signature = uint32()

    @property
    def bundles(self):
        print(self.bundle_toc)
        return iter(self.bundle_toc.values())

    def load(self, filename: Path, engine_signature: uint32 = 0, verify_engine_signature: bool = False) -> bool:
        am = ArchiveMemory.read_from_path(filename)
        retval = self.serialize(am, engine_signature, verify_engine_signature)
        self.id = filename.get_string_id()
        self.bundle_root = Path(filename.get_directory())

        return retval

    def is_bundle_registered(self, bundle_filename: String8) -> bool:
        return bundle_filename in self.bundle_toc.values()

    def find_bundle_containing(self, filename: Path) -> Path:
        file_id = filename.get_string_id()
        if file_id in self.files:
            file_link = self.files[file_id]
            ids_extractor = BundleIDsExtractor(file_link, self.bundleIds)

            assert (
                ids_extractor.get_size() > 0,
                f"File {filename} referenced but not contained in any bundle."
            )

            for i in range(ids_extractor.get_size()):
                bundle_id = ids_extractor.get_id(i)
                if bundle_id in self.bundle_toc:
                    bundle_name = self.bundle_toc[bundle_id]
                    result = Path(self.bundle_root)
                    result.change_basename(bundle_name)
                    return result
        return Path.empty_path()

    def is_fat(self, filename: Path) -> bool:
        return self.id == filename.get_string_id()

    def serialize(self, am: ArchiveMemory, engine_signature: uint32, verify_engine_signature: bool) -> bool:
        if not am.is_reading():
            return False

        signature = uint32()
        signature = am.serialize(signature)
        if signature == FILE_SIGNATURE:
            self.engine_signature = am.serialize(self.engine_signature)
            eng_signature_ok = not verify_engine_signature or (self.engine_signature == engine_signature)
            if eng_signature_ok:
                version = uint32()
                version = am.serialize(version)
                if version == FILE_VERSION:
                    bundle_offset = len(self.bundle_toc)
                    num_files = uint32()
                    num_files = am.serialize(num_files)

                    for _ in range(num_files):
                        file_id = StringID()
                        file_id.serialize(am)

                        self.files[file_id] = BundleIDsLoader(self.bundleIds, am, bundle_offset).get_link()

                    num_bundles = uint32()
                    num_bundles = am.serialize(num_bundles)
                    for _ in range(num_bundles):
                        bundle_id = uint8()
                        bundle_id = am.serialize(bundle_id)
                        bundle_name = String8()
                        bundle_name.serialize(am)
                        print(bundle_id, bundle_name)
                        self.bundle_toc[uint8(bundle_id + bundle_offset)] = bundle_name
                    return True
                # treat old versions if needed
                else:
                    print(f"[FAT] Warning: File version mismatch. Expected: {FILE_VERSION}, got: {version}")
            else:
                print(
                    f"[FAT] Warning: Engine signature mismatch. Expected: {engine_signature}, got: {self.engine_signature}")
        else:
            print(f"[FAT] Warning: Invalid file signature. Expected: {FILE_SIGNATURE}, got: {signature}")
        return False
