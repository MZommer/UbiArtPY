from typing import Iterator, Optional

from ...Core import ArchiveMemory, serializable_class
from ...__types__ import uint32, uint64, Path


@serializable_class
class FileHeader:
    # Count: uint32
    original_size: uint32
    compressed_size: uint32
    flush_time: uint64  # date
    positions: list[uint64]
    position: uint64
    file_path: Path

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

    def __init__(
            self,
            original_size: uint32 = 0,
            compressed_size: uint32 = 0,
            flush_time: uint64 = 0,
            itf_path: Path = Path.empty_path()
    ) -> None:
        """
        Arguments:
            original_size (uint32, optional): Original file size. Defaults to 0.
            compressed_size (uint32, optional): Compressed file size if not compressed, 0. Defaults to 0.
            flush_time (uint64, optional): File time. uint64 that represents the number of 100-nanosecond intervals that have elapsed since 12:00 A.M. January 1, 1601, Coordinated Universal Time (UTC). Defaults to 0.
            itf_path (Path, optional): File path inside the bundle.
        """
        self.original_size = uint32(original_size)
        self.compressed_size = uint32(compressed_size)
        self.flush_time = uint64(flush_time)
        self.position = uint64()
        self.positions = [self.position]
        self.file_path = Path(itf_path)

    def __repr__(self):
        return f"FileHeader(original_size={self.original_size}, compressed_size={self.compressed_size}, flush_time={self.flush_time}, positions={self.positions}, position={self.position}, file_path={self.file_path})"

    @property
    def count(self) -> uint32:
        return uint32(len(self.positions))

    def set_position(self, position: uint64) -> None:
        self.positions.append(position)

    def get_position(self, index: uint32) -> uint64:
        return self.positions[index]

    def compute_size(self) -> uint32:
        return uint32(4 + 4 + 4 + 8 + (8 * self.count) + self.file_path.get_serialize_size())
        # sizeof(Count) + sizeof(OriginalSize) + sizeof(CompressedSize) + sizeof(FlushTime) + sizeof(Position) * Count + path.getSerializeSize

    def serialize(self, am: ArchiveMemory) -> None:
        count = am.serialize(self.count)
        # Assert count is within valid range (4-bit value)
        assert count <= ((1 << 4) - 1), "Value overflow, position count over the valid range (4-bit value)!"
        self.original_size = am.serialize(self.original_size)
        self.compressed_size = am.serialize(self.compressed_size)
        # Assert compressed size is within valid range (28-bit value)
        assert (
            self.compressed_size <= ((1 << 28) - 1),
            "Value overflow, CompressedSize over the valid range (28-bit value)!"
        )
        self.flush_time = am.serialize(self.flush_time)

        if am.is_reading():
            # Assert count is valid before allocating positions array
            assert count >= 1, "Invalid positions count, should be at least 1!"

            if count > 1:
                self.positions = [am.serialize(uint64()) for _ in range(count)]
                self.position = self.positions[0]
            else:  # TODO: check if this if is necessary
                # For single position case
                self.position = am.serialize(uint64())
                self.positions = [self.position]
        else:
            if count > 1:
                for position in self.positions:
                    am.serialize(position)
            else:
                am.serialize(self.position)
        self.file_path.serialize(am)


class FileHeadersWrapper:
    files: dict[Path, FileHeader]

    def __init__(self) -> None:
        self.files = {}

    def add_file(self, file_header: FileHeader) -> None:
        self.files[file_header.file_path] = file_header

    def get_header(self, file_path: Path) -> Optional[FileHeader]:
        return self.files.get(file_path)

    def serialize(self, am: ArchiveMemory) -> None:
        size = am.serialize(uint32(len(self.files)))
        if am.is_reading():
            for _ in range(size):
                header = FileHeader()
                header.serialize(am)
                self.add_file(header)
        else:
            for file_header in self.files.values():
                file_header.serialize(am)

    def compute_size(self) -> uint32:
        size = uint32(4)  # count
        for file_header in self.files.values():
            size += file_header.compute_size()
        return size

    def __contains__(self, file_path: Path) -> bool:
        return file_path in self.files

    def __len__(self) -> int:
        return len(self.files)

    def __iter__(self) -> Iterator[Path]:
        return iter(self.files.keys())
