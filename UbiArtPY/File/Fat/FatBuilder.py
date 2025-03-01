from .FatConst import FILE_SIGNATURE, FILE_VERSION
from .__types__ import FileSet, TOC8
from ...Core import ArchiveMemory, Versioning
from ...__types__ import StringID, Path, String8, uint8, uint32


class FatBuilder:
    files: FileSet

    def __init__(self) -> None:
        self.files = {}

    def reference_file(self, path: Path, bundle_filename: String8) -> None:
        path = Path(path)
        bundle_filename = String8(bundle_filename)
        if path not in self.files:
            self.files[path] = set()
        self.files[path].add(bundle_filename)

    def save(self, filename: Path) -> bool:
        retval: bool = False
        with open(filename, 'wb') as f:
            bundle_id = uint8()
            bundle_toc: TOC8 = {}
            bundle_ids: list[uint8] = []

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
            engine_signature = uint32(Versioning.EngineSignature)
            am.serialize(engine_signature)
            version = uint32(FILE_VERSION)
            am.serialize(version)

            size = uint32(len(self.files))
            am.serialize(size)

            string_ids: dict[StringID, Path] = {}

            for path in self.files.keys():
                file_id: StringID = path.get_string_id()
                if file_id in string_ids:
                    raise FileExistsError(
                        f"Duplicate StringID {file_id} (hash collision):\n {path}\n{string_ids[file_id]}\nPlease rename one of these files."
                    )
                string_ids[file_id] = path

            for path, bundles in self.files.items():
                file_id: StringID = path.get_string_id()
                file_id.serialize(am)

                for bundle in bundles:
                    if bundle not in bundle_toc:
                        # Assert to prevent integer overflow
                        assert bundle_id != 255, "Integer overflow"
                        current_bundle_id: uint8 = bundle_id
                        bundle_id += 1
                        bundle_toc[bundle] = current_bundle_id
                    else:
                        current_bundle_id = bundle_toc[bundle]
                    bundle_ids.append(current_bundle_id)

                size = uint32(len(bundle_ids))
                am.serialize(size)
                for bundle_id in bundle_ids:
                    am.serialize(bundle_id)
                bundle_ids.clear()

            size = uint32(len(bundle_toc))
            am.serialize(size)

            for bundle_name, bundle_id in bundle_toc.items():
                am.serialize(bundle_id)
                bundle_name.serialize(am)

            retval = bool(f.write(am.get_data()))
        return retval
