from dataclasses import dataclass
from ...__types__ import uint32, uint64, Path, Platform, Platforms
from ...Core import ArchiveMemory
from .BundleHeader import BundleHeader
from .FileHeader import FileHeader, FileHeadersWrapper
from io import BytesIO
import os.path
from ..FileHelpers import get_windows_file_timestamps, override_timestamps
from ..Compress import Compress

FILES_TO_COMPRESS = ".s3d.ckd", ".a3d.ckd", ".m3d.ckd", ".tga.ckd", ".png.ckd", ".anm.ckd", ".fx.fxb", ".dtape.ckd"
CHUNK_LENGTH = 1024*1024

@dataclass(frozen=True, slots=True)
class RegisteredFile:
    abspath: Path
    itfpath: Path
    compress: bool
    flushtime: uint64

class PackFile: # IPK (ITF Pack)
    Header: BundleHeader
    Files: FileHeadersWrapper
    _archive: ArchiveMemory
    _mode: str
    _register: dict[Path, RegisteredFile]
    
    # create zip library like way to compress/decompress
    def __init__(self, path: Path, mode: str, platform: Platform = Platforms.INVALID, binary: bool = False, data_version: uint32 = uint32()) -> None:
        """Wrapper for IPK handling. Remember to set up the engine enviroment (Bundle & Engine versions).
        
        Args:
            path (Path): Path to IPK file.
            mode (str): Open mode, "r" read, "w" write, "a" append.
            platform (Platform, optional): Platform for write mode. Default Platforms.INVALID.
            binary (bool, optional): Binary (Scene/Logic) for write mode. Default False.
        """
        self.Header = BundleHeader(platform, binary, data_version)
        self.Files = FileHeadersWrapper()
        path = Path(path)
        mode = mode.lower()
        if mode == "r" or mode == "a":
            self._archive = ArchiveMemory.read_from_path(path)
            self.Header.serialize(self._archive)
            self.Files.serialize(self._archive)
        elif mode == "w":
            self._register = {}
            self._archive = ArchiveMemory.write_from_path(path)
    
    # Read methods
    def extract(self, folder: Path, file: FileHeader, overwrite: bool = True) -> None:
        """Extracts a file from the IPK to the given folder.

        Args:
            folder (Path): Folder to extract to.
            file (Path): File to extract.
            overwrite (bool, optional): Overwrite existing file. Default False.
        """
        
        if not self._archive.isReading():
            raise PermissionError("File is not open for reading.")
        
        folder = Path(folder)
        file = Path(file)
        
        header = self.Files.get_header(file)
        if header is None:
            raise FileNotFoundError(f"File {file} not found in IPK.")
        
        abspath = folder.copyAndAppend(file)
        if not overwrite:
            if os.path.isfile(abspath):
                return # skipping file
        os.makedirs(abspath.getDirectory(), exist_ok=True)  # create directory
        
        with open(abspath, "wb") as f:
            self._archive.seek(self.Header.FilesStart + header.Position)
            if header.CompressedSize != 0:
                self._extract_compressed(header, f)
            else:
                # TODO: add write chunks for big files
                data = self._archive.serializeBlock8(None, header.OriginalSize)
                f.write(data)
            override_timestamps(abspath, header.FlushTime, header.FlushTime)
    
    def _extract_compressed(self, header: FileHeader, stream: BytesIO) -> None:
        """Extracts a compressed file from the IPK to the given folder.

        Args:
            header (FileHeader): Header of the file to extract.
            stream: (BytesIO): File stream to write.
        """
        if header.CompressedSize == 0:
            raise ValueError(f"File {header.FilePath} is not compressed.")
        compressed = self._archive.serializeBlock8(None, header.CompressedSize)
        data = Compress.uncompress_buffer_zlib(compressed)
        if len(data) != header.OriginalSize:
            raise OverflowError(f"File {header.FilePath} is corrupted. Expected size {header.OriginalSize} but got {len(data)}")
        stream.write(data)
    
    def extract_all(self, folder: Path, overwrite: bool = False) -> None:
        """Extracts all files from the IPK to the given folder.

        Args:
            folder (Path): Folder to extract to.
            overwrite (bool, optional): Overwrite existing files. Default False.
        """
        for file in self.Files:
            self.extract(folder, file, overwrite)
    
    # Write methods
    def register_file(self, file: Path, itfpath: Path, force_compress: bool = False) -> None:
        """Registers a file to the IPK.

        Args:
            file (Path): Path to the file to register.
            arcpath (Path): Path to the file in the IPK.
            force_compress (bool): Force file compression.
        """
        if self._archive.isReading():
            raise PermissionError("File is not open for writing.")

        file = Path(file)
        itfpath = Path(itfpath)
        
        if self._register.get(itfpath) is not None:
            raise FileExistsError(f"File {itfpath} is already registered.")
        
        # TODO: add lock file when registered and unlock when __exit__
        compressed = PackFile.judge_compression(file) if not force_compress else force_compress
        creation, modified, access = get_windows_file_timestamps(file)
        rfile = RegisteredFile(file, itfpath, compressed, modified)
        self._register[itfpath] = rfile
    
    @staticmethod
    def judge_compression(file: Path) -> bool:
        basename: str = file.getBasename()
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
        if self._archive.isReading():
            raise PermissionError("File is not open for writing.")
        
        for rfile in self._register.values():
            header = FileHeader(flush_time=rfile.flushtime, itf_path=rfile.itfpath)
            self.Files.add_file(header)

        self.Header.FilesStart = self.Header.compute_size() + self.Files.compute_size()
        self.Header.FilesCount = uint32(len(self.Files))        
        self._archive.reserve(self.Header.FilesStart)
        

        for rfile in self._register.values():
            header = self.Files.get_header(rfile.itfpath)
            if not header:
                print(f"File {rfile.itfpath} not found in IPK.")
                continue
            with open(rfile.abspath, "rb") as f:
                data = f.read()
                size = uint32(f.tell())
                header.OriginalSize = uint32(size)
                
                # TODO: Add file replication for discs
                header.Position = uint64(self._archive.getSeekPos())
                header.Positions.append(header.Position)
                
                if rfile.compress:
                    data = Compress.compress_buffer_zlib(data)
                    size = uint32(len(data))
                    header.CompressedSize = size
                # TODO: Add read and write in chunks to optimize big files
                self._archive.serializeBlock8(data, size)
        
        self._archive.seek(0)
        self.Header.serialize(self._archive)
        self.Files.serialize(self._archive)
        
        self._archive.close()
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def __enter__(self):
        return self
    
    # Append methods
