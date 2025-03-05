import struct
from io import BytesIO
from typing import Optional, Union, Any, BinaryIO

from BinaryHelper import get_type_format, get_sizeof, Endianess

from ..__types__ import (
    Path,
    int8, uint8, int16, uint16, uint32, int32,
    uint64, int64, float32, float64,
)


def archive_roundup(x: int, a: int) -> int:
    return (x + (a - 1)) & (~(a - 1))


class ArchiveMemory:
    data: BinaryIO
    seek_pos: uint32
    capacity: uint32
    size: uint32
    linker: "ArchiveLinker"
    _is_reading: bool
    byte_order: Endianess
    strict: bool

    def __init__(
            self,
            is_reading: bool = False,
            size: uint32 = 0,
            reserve: uint32 = 0,
            buffer: Optional[bytes] = None,
            byteorder: Endianess = Endianess.BIG,
            strict=False
    ):
        self.data = BytesIO()
        self.seek_pos = uint32()
        self.capacity = uint32()
        self.size = uint32()
        # Using uint since all the platforms work with fat32, add warning if reached since limit is 4gb.
        self.linker = None  # Not implemented.
        self._is_reading = is_reading
        self.byte_order = byteorder
        self.strict = strict
        if buffer:
            self.init(len(buffer), size, True)
            self.data = BytesIO(bytearray(buffer))
        elif reserve > 0:
            self.init(reserve, size, is_reading)

    def init(self, reserve: uint32, size: uint32, is_reading: bool):
        self.reserve(reserve)
        self.size = uint32(size)
        self._is_reading = uint32(is_reading)

    def close(self):
        self.data.close()

    def __enter__(self):
        return self

    def __del__(self):
        self.close()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    @staticmethod
    def read_from_path(path: Path, byteorder: Endianess = Endianess.BIG) -> "ArchiveMemory":
        f = open(path, 'rb')
        length = uint32(f.seek(0, 2))
        f.seek(0)
        am = ArchiveMemory(True, length, byteorder=byteorder)
        am.data = f
        am.rewind_for_reading()
        return am

    @staticmethod
    def write_from_path(path: Path, byteorder: Endianess = Endianess.BIG) -> "ArchiveMemory":
        f = open(path, 'wb')
        am = ArchiveMemory(False, 0, byteorder=byteorder)
        am.data = f
        am.rewind_for_writing()
        return am

    def reserve(self, new_capacity: uint32):
        if self.capacity < new_capacity:
            # Increase capacity by adding more bytes
            self.data.seek(0, 2)  # Move to the end of the current stream
            self.data.write(b'\x00' * (new_capacity - self.capacity))
            self.data.seek(0)  # Go back to start
        self.capacity = new_capacity

    def get_capacity(self) -> uint32:
        return self.capacity

    def get_size(self) -> uint32:
        return self.size

    def get_seek_pos(self) -> uint32:
        return self.seek_pos

    def get_data(self) -> bytes:
        return self.data.getvalue()

    def get_ptr(self) -> BinaryIO:
        return self.data

    def clear(self):
        self.data = BytesIO()
        self.seek_pos = uint32(0)
        self.size = uint32(0)
        self.capacity = uint32(0)

    def set_writing(self):
        self._is_reading = False

    def is_reading(self) -> bool:
        return self._is_reading

    def is_strict(self) -> bool:
        return self.strict

    def rewind_for_writing(self):
        self.data.seek(0)
        # self.m_pData.truncate()
        self.seek_pos = uint32()
        self.size = uint32()

    def rewind_for_reading(self):
        self.data.seek(0)
        self._is_reading = True

    def get_info(self) -> tuple[uint32, uint32]:
        return self.get_size(), self.get_seek_pos()

    def seek(self, pos: int):
        self.data.seek(pos)
        self.seek_pos = uint32(pos)

    def pad_seek_pos_on32(self):
        self.seek_pos = archive_roundup(self.seek_pos, 4)

    def serialize_internal_buffer(self, buffer: bytes, size: int):
        if self.is_reading():
            buffer = self.data.read(size)
            return buffer
        else:
            # Check if we need to increase capacity
            if size + self.size > self.capacity:
                self.reserve(size + self.size)

            # Write the buffer at current position
            self.data.seek(self.seek_pos)
            self.data.write(buffer[:size])

            # Calculate new seek position
            seek_pos = self.seek_pos + size

            # Update size if seek_pos is beyond current size
            if seek_pos >= self.size:
                self.size = seek_pos

            # Update seek position
            self.seek_pos = seek_pos
            return buffer

    def serialize(self,
                  ptr: Union[int8, uint8, int16, uint16, uint32, int32, uint64, int64, float32, float64]
                  ) -> Any:
        _dtype = type(ptr)
        if _dtype is bool:
            _dtype = uint32
            ptr = uint32(ptr)
        size = get_sizeof(ptr)
        bytes_format = get_type_format(self.byte_order) + get_type_format(_dtype)
        buffer = struct.pack(bytes_format, ptr)
        buffer = self.serialize_internal_buffer(buffer, size)
        if self.is_reading():
            ptr = _dtype(struct.unpack(bytes_format, buffer)[0])
        return ptr

    def serialize_block8(self, buffer: Optional[bytes], size: int):
        buffer = self.serialize_internal_buffer(buffer, size)
        return buffer

    # TODO: Implement ArchiveLinker methods


class ArchiveLinker:
    m_pArchive: ArchiveMemory
    m_bReading: bool
    m_References: dict[int, int]  # Mapping from 32-bit pointers to Python objects (uPtr)

    def __init__(self, archive: ArchiveMemory):
        self.m_pArchive = archive
        self.m_bReading = archive.is_reading()
        self.m_References = {}

    def get_link(self, ptr: int) -> Optional[Union[int, float, bytes]]:
        # In Python, we just return the reference from the dictionary
        if ptr not in self.m_References:
            return None
        return self.m_References[ptr]

    def serialize(self, ptr: Union[int, float, bytes]):
        ptr_value = uint32(ptr)
        if self.m_bReading:
            ptr_value = self.m_pArchive.serialize(ptr_value)
            self.m_References[ptr_value] = ptr
        else:
            self.m_pArchive.serialize(ptr_value)
