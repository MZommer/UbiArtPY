from ...__types__ import StringID, Path, String8, uint8, uint32
from .FatConst import FILE_SIGNATURE, FILE_VERSION
from ...Core import ArchiveMemory
from .__types__ import BundleTOC, BundleIds, FileLink, FileLinks
from .FatConst import IndexToBundleIdsArray_Mask

class BundleIDsLoader:
    m_fileLink: FileLink
    
    def __init__(self, bundle_ids: BundleIds, am: ArchiveMemory, offset_pos: uint32) -> None:
        bundles = uint32()
        bundles = am.serialize(bundles)
        
        self.m_fileLink.bundleId.m_idActive = bundles == 1
        
        if self.m_fileLink.bundleId.m_idActive:
            bundleId = uint8()
            bundleId = am.serialize(bundleId)
            self.m_fileLink.bundleId.m_id = bundleId + offset_pos
        else:
            idxInBundlesArray = uint32(list(bundle_ids))
            assert idxInBundlesArray <=  IndexToBundleIdsArray_Mask, "Value overflow! Please check FileLink structure!"
            self.m_fileLink.bundleIds.m_index = idxInBundlesArray & IndexToBundleIdsArray_Mask
            bundle_ids.append(bundles)
            for _ in range(bundles):
                bundleId = uint8()
                bundleId = am.serialize(bundleId)
                bundle_ids.append(uint8(bundleId + offset_pos))
    
    def getLink(self) -> FileLink:
        return self.m_fileLink
        
    def get_size(self) -> uint32:
        return self.m_bundleIds.get_size()
    
    def get_id(self, index: uint32) -> uint8:
        return self.m_bundleIds.get_index(index)

class BundleIDsExtractor:
    m_fileLink: FileLink
    m_bundleIds: BundleIds
    
    def __init__(self, file_link: FileLink, bundle_ids: BundleIds) -> None:
        self.m_fileLink = file_link
        self.m_bundleIds = bundle_ids
    
    def get_size(self) -> uint32:
        return len(self.m_bundleIds)

    def get_id(self, index: uint32) -> uint8:
        return self.m_bundleIds[index]

class FatBase:
    m_bundleTOC: BundleTOC
    m_files: FileLinks
    m_bundleIds: BundleIds
    m_bundleRoot: Path
    m_id: StringID
    m_engineSignature: uint32
    
    def __init__(self) -> None:
        self.m_bundleTOC = BundleTOC()
        self.m_files = FileLinks()
        self.m_bundleIds = BundleIds
        self.m_bundleRoot = Path()
        self.m_id = StringID()
        self.m_engineSignature = uint32()

    def load(self, filename: Path, engine_signature: uint32, verify_engine_signature: bool) -> bool:
        retval: bool = False
        
        try:
            with open(filename, 'rb') as f:
                length = uint32(f.seek(0, 2))
                f.seek(0)
                am = ArchiveMemory(length, length, True)
                f.readinto(am.getPtrForWrite())
                am.rewindForReading()
                
                retval = self.serialize(am, engine_signature, verify_engine_signature)
                self.m_id = filename.getStringID()
                self.m_bundleRoot = filename.getDirectory()
        except:
            pass
        
        return retval

    def isBundleRegistered(self, bundle_filename: String8) -> bool:
        return bundle_filename in self.m_bundleTOC.values()

    def findBundleContaining(self, filename: Path) -> Path:
        file_id = filename.getStringID()
        if file_id in self.m_files:
            file_link = self.m_files[file_id]
            ids_extractor = BundleIDsExtractor(file_link, self.m_bundleIds)

            assert ids_extractor.get_size() > 0, f"File {filename} referenced but not contained in any bundle."
            
            for i in range(ids_extractor.get_size()):
                bundle_id = ids_extractor.get_id(i)
                if bundle_id in self.m_bundleTOC:
                    bundle_name = self.m_bundleTOC[bundle_id]
                    result = Path(self.m_bundleRoot)
                    result.changeBasename(bundle_name)
                    return result
        return Path.EmptyPath
    
    def is_fat(self, filename: Path) -> bool:
        return self.m_id == filename.getStringID()

    def serialize(self, am: ArchiveMemory, engine_signature: uint32, verify_engine_signature: bool) -> bool:
        if not am.isReading():
            return False

        signature = uint32()
        signature = am.serialize(signature)
        if signature == FILE_SIGNATURE:
            self.m_engineSignature = am.serialize(self.m_engineSignature)
            eng_signature_ok = not verify_engine_signature or (self.m_engineSignature == engine_signature)
            if eng_signature_ok:
                version = uint32()
                version = am.serialize(version)
                if version == FILE_VERSION:
                    bundle_offset = len(self.m_bundleTOC)
                    num_files = uint32()
                    num_files = am.serialize(num_files)

                    for _ in range(num_files):
                        file_id = StringID()
                        file_id.serialize(am)
                        
                        self.m_files[file_id] = BundleIDsLoader(self.m_bundleIds, am, bundle_offset).get_link()

                    num_bundles = uint32()
                    num_bundles = am.serialize(num_bundles)
                    for _ in range(num_bundles):
                        bundle_id = uint8()
                        bundle_id = am.serialize(bundle_id)
                        bundle_name = String8()
                        bundle_name.serialize(am)
                        self.m_bundleTOC[uint8(bundle_id + bundle_offset)] = bundle_name
                    return True
                # treat old versions if needed
                else:
                    print(f"[FAT] Warning: File version mismatch. Expected: {FILE_VERSION}, got: {version}")
            else:
                print(f"[FAT] Warning: Engine signature mismatch. Expected: {engine_signature}, got: {self.m_engineSignature}")
        else:
            print(f"[FAT] Warning: Invalid file signature. Expected: {FILE_SIGNATURE}, got: {signature}")
        return False
