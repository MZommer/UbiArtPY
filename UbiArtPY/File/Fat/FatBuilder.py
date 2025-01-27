from ...__types__ import StringID, Path, String8, uint8, uint32
from .FatConst import FILE_SIGNATURE, FILE_VERSION
from ...Core import ArchiveMemory, Versioning
from .__types__ import FileSet, TOC8, BundleSet

class FatBuilder:
    m_files: FileSet
    
    def __init__(self) -> None:
        self.m_files = FileSet()
    
    def referenceFile(self, path: Path, bundleFilename: String8) -> None:
        path = Path(path)
        bundleFilename = String8(bundleFilename)
        if path not in self.m_files:
            self.m_files[path] = BundleSet()
        self.m_files[path].add(bundleFilename)
    
    def save(self, filename: Path) -> bool:
        retval: bool = False
        with open(filename, 'wb') as f:
            bundleId = uint8()
            bundleTOC = TOC8()
            bundleIds: list[uint8] = []
            
            # FILE_SIGNATURE
            # ENGINE_SIGNATURE
            # FILE_VERSION
            # FileTOC
            #  Count
            #  Filename id (CRC of the full path)
            #  Bundle count
            #  Bundle ids
            # BundleTOC
            #  Count
            #  Bundle id
            #  Bundle filename
            
            am = ArchiveMemory()
            signature = uint32(FILE_SIGNATURE)
            am.serialize(signature)
            engSignature = uint32(Versioning.EngineSignature)
            am.serialize(engSignature)
            version = uint32(FILE_VERSION)
            am.serialize(version)

            size = uint32(len(self.m_files))
            am.serialize(size)
            
            stringIDs = dict[StringID, Path]()
            
            for path in self.m_files.keys():
                fileId: StringID = path.getStringID()
                if fileId in stringIDs:
                    raise FileExistsError(f"Duplicate StringID {fileId.GetValue()} (hash collision):\n {path}\n{stringIDs[fileId]}\nPlease rename one of these files.")
                stringIDs[fileId] = path
            
            for path, bundles in self.m_files.items():
                fileId: StringID = path.getStringID()
                fileId.serialize(am)
                
                for bundle in bundles:
                    if bundle not in bundleTOC:
                        # Assert to prevent integer overflow
                        assert bundleId != 255, "Integer overflow"
                        currentBundleId: uint8 = bundleId
                        bundleId += 1
                        bundleTOC[bundle] = currentBundleId
                    else:
                        currentBundleId = bundleTOC[bundle]
                    bundleIds.append(currentBundleId)
                
                size = uint32(len(bundleIds))
                am.serialize(size)
                for bundleId in bundleIds:
                    am.serialize(bundleId)
                bundleIds.clear()
            
            size = uint32(len(bundleTOC))
            am.serialize(size)
            
            for bundle_name, bundle_id in bundleTOC.items():
                am.serialize(bundle_id)
                bundle_name.serialize(am)
            
            retval = bool(f.write(am.getData()))
        return retval
