from ...__types__ import uint32, uint64, Path
from ...Core import ArchiveMemory, SerializableClass
from typing import Iterator

@SerializableClass
class FileHeader:
    # Count: uint32
    OriginalSize: uint32
    CompressedSize: uint32
    FlushTime: uint64  # date
    Positions: list[uint64]
    Position: uint64
    FilePath: Path
    
    """
    Position vs Positions in FileHeader
    =================================

    Single Position (m_Position):
    ---------------------------
    - Used when Count == 1
    - Direct access to position value
    - Lighter memory footprint
    - Best for:
        * Small files
        * Non-critical data
        * SSD storage where seek time isn't critical
        * When redundancy isn't needed

    Multiple Positions (m_Positions):
    ------------------------------
    - Used when Count > 1
    - Array of positions for same data
    - Same size applies to all positions
    - Best for:
        * Critical game data needing redundancy
        * Frequently accessed files
        * HDD optimization (reducing seek times)
        * Streaming optimization
        * Platform-specific optimizations

    Usage Example:
        Single:   [Position: 1000] Size: 500
            -> Data stored once at offset 1000

        Multiple: [Positions: 1000, 2000, 3000] Size: 500
            -> Same data stored at all three offsets
            -> Reader picks closest position to current file pointer
    """
    
    def __init__(self, original_size: uint32 = 0, compressed_size: uint32 = 0, flush_time: uint64 = 0, itf_path: Path = Path("")) -> None:
        """
        Args:
            original_size (uint32, optional): Original file size. Defaults to 0.
            compressed_size (uint32, optional): Compressed file size if not compressed, 0. Defaults to 0.
            flush_time (uint64, optional): File time. uint64 that represents the number of 100-nanosecond intervals that have elapsed since 12:00 A.M. January 1, 1601 Coordinated Universal Time (UTC). Defaults to 0.
            itf_path (Path, optional): File path inside the bundle.
        """
        self.OriginalSize = uint32(original_size)
        self.CompressedSize = uint32(compressed_size)
        self.FlushTime = uint64(flush_time)
        self.Positions = []
        self.Position = uint64()
        self.FilePath = Path(itf_path)
    
    def __repr__(self):
        return f"FileHeader(OriginalSize={self.OriginalSize}, CompressedSize={self.CompressedSize}, FlushTime={self.FlushTime}, Positions={self.Positions}, Position={self.Position}, FilePath={self.FilePath})"
    
    @property
    def Count(self) -> uint32:
        if self.Position:
            return uint32(1) # Single position case
        return uint32(len(self.Positions))
    
    def set_position(self, position: uint64) -> None:
        self.Positions.append(position)
    
    def get_position(self, index: uint32) -> uint64:
        return self.Positions[index]
    
    def compute_size(self) -> uint32:
        return uint32(4 + 4 + 4 + 8 + 8 * self.Count + len(self.FilePath))
        # sizeof(Count) + sizeof(OriginalSize) + sizeof(CompressedSize) + sizeof(FlushTime) + sizeof(Position) * Count + path.size

    def serialize(self, am: ArchiveMemory) -> None:
        count = am.serialize(self.Count)
        # Assert count is within valid range (4-bit value)
        assert count <= ((1 << 4) - 1), "Value overflow, position count over the valid range (4-bit value)!"
        self.OriginalSize = am.serialize(self.OriginalSize)
        self.CompressedSize = am.serialize(self.CompressedSize)
        # Assert compressed size is within valid range (28-bit value)
        assert self.CompressedSize <= ((1 << 28) - 1), "Value overflow, CompressedSize over the valid range (28-bit value)!"
        self.FlushTime = am.serialize(self.FlushTime)
        
        if am.isReading():
            # Assert count is valid before allocating positions array
            assert count >= 1, "Invalid positions count, should be at least 1!"
            
            if count > 1:
                self.Positions = [am.serialize(uint64()) for _ in range(count)]
            else:
                # For single position case
                self.Position = am.serialize(uint64())
                self.Positions = [self.Position]
        else:
            if count > 1:
                for position in self.Positions:
                    am.serialize(position)
            else:
                am.serialize(self.Position)
        self.FilePath.serialize(am)

class FileHeadersWrapper:
    Files: dict[Path, FileHeader]
    
    def __init__(self) -> None:
        self.Files = {}
    
    def add_file(self, file_header: FileHeader) -> None:
        self.Files[file_header.FilePath] = file_header
    
    def get_header(self, file_path: Path) -> FileHeader | None:
        return self.Files.get(file_path)
    
    def serialize(self, am: ArchiveMemory) -> None:
        size = am.serialize(uint32(len(self.Files)))
        if am.isReading():
            for _ in range(size):
                header = FileHeader()
                header.serialize(am)
                self.add_file(header)
        else:
            for file_header in self.Files.values():
                file_header.serialize(am)
    
    def compute_size(self) -> uint32:
        size = uint32(4) # count
        for file_header in self.Files.values():
            size += file_header.compute_size()
        return size
    
    def __contains__(self, file_path: Path) -> bool:
        return file_path in self.Files
    
    def __len__(self) -> int:
        return len(self.Files)
    
    def __iter__(self) -> Iterator[Path]:
        return iter(self.Files.keys())