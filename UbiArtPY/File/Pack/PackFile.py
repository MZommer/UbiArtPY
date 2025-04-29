import os.path
from dataclasses import dataclass
from typing import BinaryIO

from .BundleHeader import BundleHeader
from .FileHeader import FileHeader, FileHeadersWrapper
from ..Compress import Compress
from ..FileHelpers import get_windows_file_timestamps, override_timestamps
from ...Core.Archive import ArchiveMemory
from ...__types__ import uint32, uint64, Path, Platform, Platforms, PathType

FILES_TO_COMPRESS = ".s3d.ckd", ".a3d.ckd", ".m3d.ckd", ".tga.ckd", ".png.ckd", ".anm.ckd", ".fx.fxb", ".dtape.ckd"
CHUNK_LENGTH = 1024 * 1024


@dataclass(frozen=True, slots=True)
class RegisteredFile:
    abs_path: Path
    itf_path: Path
    compress: bool
    flush_time: uint64


class PackFile:  # IPK (ITF Pack)
    header: BundleHeader
    files: FileHeadersWrapper
    _archive: ArchiveMemory
    _mode: str
    _register: dict[Path, RegisteredFile]

    # create zip library like way to compress/decompress
    def __init__(self,
                 path: PathType,
                 mode: str,
                 platform: Platform = Platforms.INVALID,
                 binary: bool = False,
                 data_version: uint32 = uint32()
                 ) -> None:
        """
        Wrapper for IPK handling. Remember to set up the engine environment (Bundle & Engine versions).
        
        Args:
            path (Path): Path to IPK file.
            mode (str): Open mode, "r" read, "w" write, "a" append.
            platform (Platform, optional): Platform for write mode. Default Platforms.INVALID.
            binary (bool, optional): Binary (Scene/Logic) for write mode. Default False.
        """
        self.header = BundleHeader(platform, binary, data_version)
        self.files = FileHeadersWrapper()
        path = Path(path)
        mode = mode.lower()
        if mode == "r" or mode == "a":
            self._archive = ArchiveMemory.read_from_path(path)
            self.header.serialize(self._archive)
            self.files.serialize(self._archive)
        elif mode == "w":
            self._register = {}
            self._archive = ArchiveMemory.write_from_path(path)

    # Read methods
    def extract(self, folder: Path, file: Path, overwrite: bool = True) -> None:
        """
        Extracts a file from the IPK to the given folder.

        Args:
            folder (Path): Folder to extract to.
            file (Path): File to extract.
            overwrite (bool, optional): Overwrite existing file. Default False.
        """

        if not self._archive.is_reading():
            raise PermissionError("File is not open for reading.")

        folder = Path(folder)
        file = Path(file)

        header = self.files.get_header(file)
        if header is None:
            raise FileNotFoundError(f"File {file} not found in IPK.")

        abs_path = folder.copy_and_append(file)
        if not overwrite:
            if os.path.isfile(abs_path):
                return  # skipping file
        os.makedirs(abs_path.get_directory(), exist_ok=True)  # create directory

        with open(abs_path, "wb") as f:
            self._archive.seek(self.header.files_start + header.position)
            if header.compressed_size != 0:
                self._extract_compressed(header, f)
            else:
                # TODO: add write chunks for big files
                data = self._archive.serialize_block8(None, header.original_size)
                f.write(data)
            override_timestamps(abs_path, header.flush_time, header.flush_time)

    def _extract_compressed(self, header: FileHeader, stream: BinaryIO) -> None:
        """
        Extracts a compressed file from the IPK to the given folder.

        Args:
            header (FileHeader): Header of the file to extract.
            stream: (BytesIO): File stream to write.
        """
        if header.compressed_size == 0:
            raise ValueError(f"File {header.file_path} is not compressed.")
        compressed = self._archive.serialize_block8(None, header.compressed_size)
        data = Compress.uncompress_buffer_zlib(compressed)
        if len(data) != header.original_size:
            raise OverflowError(
                f"File {header.file_path} is corrupted. Expected size {header.original_size} but got {len(data)}"
            )
        stream.write(data)

    def extract_all(self, folder: Path, overwrite: bool = False) -> None:
        """
        Extracts all files from the IPK to the given folder.

        Args:
            folder (Path): Folder to extract to.
            overwrite (bool, optional): Overwrite existing files. Default False.
        """
        for file in self.files:
            try:
                self.extract(folder, file, overwrite)
            except Exception as e:
                raise BufferError(f"Error while extracting in pos {self._archive.get_seek_pos()}", e)

    # Write methods
    def register_file(self, file: Path, itf_path: Path, force_compress: bool = False):
        """
        Registers a file to the IPK.

        Args:
            file (Path): Path to the file to register.
            itf_path (Path): Path to the file in the IPK.
            force_compress (bool): Force file compression.
        """
        if self._archive.is_reading():
            raise PermissionError("File is not open for writing.")

        file = Path(file)
        itf_path = Path(itf_path)

        if self._register.get(itf_path) is not None:
            raise FileExistsError(f"File {itf_path} is already registered.")

        # TODO: add lock file when registered and unlock when __exit__
        compressed = PackFile.judge_compression(file) if not force_compress else force_compress
        creation, modified, access = get_windows_file_timestamps(file)
        rfile = RegisteredFile(file, itf_path, compressed, modified)
        self._register[itf_path] = rfile

    @staticmethod
    def judge_compression(file: Path) -> bool:
        basename: str = file.get_basename()
        compressed = any(basename.endswith(suffix) for suffix in FILES_TO_COMPRESS)

        if basename.endswith(".webm"):
            return False

        if compressed:
            with open(file, "rb") as f:
                size = f.seek(0, 2)
                if size < 32 * 1024:
                    return False

        return compressed

    def save(self):
        if self._archive.is_reading():
            raise PermissionError("File is not open for writing.")

        for rfile in self._register.values():
            header = FileHeader(flush_time=rfile.flush_time, itf_path=rfile.itf_path)
            self.files.add_file(header)

        self.header.files_start = self.header.compute_size() + self.files.compute_size()
        self.header.files_count = uint32(len(self.files))
        self._archive.reserve(self.header.files_start)
        self._archive.seek(self.header.files_start)

        for rfile in self._register.values():
            header = self.files.get_header(rfile.itf_path)
            if not header:
                print(f"File {rfile.itf_path} not found in IPK.")
                continue
            with open(rfile.abs_path, "rb") as f:
                data = f.read()
                size = uint32(f.tell())
                header.original_size = uint32(size)
                # TODO: Add file replication for discs
                header.position = uint64(self._archive.get_seek_pos() - self.header.files_start)
                header.positions = [header.position]

                if rfile.compress:
                    data = Compress.compress_buffer_zlib(data)
                    size = uint32(len(data))
                    header.compressed_size = size
                # TODO: Add read and write in chunks to optimize big files
                self._archive.serialize_block8(data, size)

        self._archive.rewind_for_writing()
        self.header.serialize(self._archive)
        self.files.serialize(self._archive)

        self._archive.close()

    def close(self):
        self._archive.close()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __enter__(self):
        return self

    # Append methods
