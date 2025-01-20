import struct
from typing import Optional, Union
from io import BytesIO
from ..__types__ import Path, int8, uint8, int16, uint16, uint32, int32, float32, float64, dtype
from BinaryHelper import get_type_format, get_sizeof, Endianess

def archive_roundup(x: int, a: int) -> int:
    return ((x + (a - 1)) & (~(a - 1)))

class ArchiveMemory:
    def __init__(self, isReading: bool = False, size: uint32 = 0, reserve: uint32 = 0, pBuffer: Optional[bytes] = None, byteorder: Endianess = Endianess.BIG, strict = False):
        self.m_pData = BytesIO()
        self.m_iSeekPos = uint32(0)
        self.m_iCapacity = uint32(0)
        self.m_iSize = uint32(0)  # uisng uint since all the platforms work with fat32, add warning if reached since limit is 4gb.
        self.m_Linker = None
        self.m_isReading = isReading
        self.m_byteorder = byteorder
        self.m_strict = strict
        if pBuffer:
            self.init(len(pBuffer), size, True)
            self.m_pData = BytesIO(bytearray(pBuffer))
        elif reserve > 0:
            self.init(reserve, size, isReading)
    
    def init(self, _reserve: uint32, _size: uint32, _isReading: bool):
        self.reserve(_reserve)
        self.m_iSize = uint32(_size)
        self.m_isReading = uint32(_isReading)
    
    def close(self):
        self.m_pData.close()
    
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
        # f.readinto(am.getPtrForWrite())
        am.m_pData = f
        am.rewindForReading()
        return am
    
    @staticmethod
    def write_from_path(path: Path, byteorder: Endianess = Endianess.BIG) -> "ArchiveMemory":
        f = open(path, 'wb')
        am = ArchiveMemory(False, 0, byteorder=byteorder)
        am.m_pData = f
        am.rewindForWriting()
        return am
    
    def reserve(self, _newCapacity: uint32):
        if self.m_iCapacity < _newCapacity:
            # Increase capacity by adding more bytes
            self.m_pData.seek(0, 2)  # Move to the end of the current stream
            self.m_pData.write(b'\x00' * (_newCapacity - self.m_iCapacity))
            self.m_pData.seek(0)  # Go back to start
        self.m_iCapacity = _newCapacity
    
    def getCapacity(self) -> uint32:
        return self.m_iCapacity
    
    def getSize(self) -> uint32:
        return self.m_iSize
    
    def getSeekPos(self) -> uint32:
        return self.m_iSeekPos
    
    def getData(self) -> bytes:
        return self.m_pData.getvalue()
    
    def getPtrForWrite(self) -> BytesIO:
        return self.m_pData
    
    def clear(self):
        self.m_pData = BytesIO()
        self.m_iSeekPos = uint32(0)
        self.m_iSize = uint32(0)
        self.m_iCapacity = uint32(0)
    
    def setWriting(self):
        self.m_isReading = False
    
    def isReading(self) -> bool:
        return self.m_isReading
    
    def isStrict(self) -> bool:
        return self.m_strict
    
    def rewindForWriting(self):
        self.m_pData.seek(0)
        self.m_pData.truncate()
        self.m_iSeekPos = uint32()
        self.m_iSize = uint32()
    
    def rewindForReading(self):
        self.m_pData.seek(0)
        self.m_isReading = True
    
    def getInfo(self) -> tuple[uint32, uint32]:
        return self.getSize(), self.getSeekPos()
    
    def seek(self, _pos: uint32):
        self.m_pData.seek(_pos)
        self.m_iSeekPos = uint32(_pos)
    
    def padSeekPosOn32(self):
        self.m_iSeekPos = archive_roundup(self.m_iSeekPos, 4)
    
    def serializeInternalBuffer(self, _pBuffer: bytes, _size: uint32):
        if self.isReading():
            _pBuffer = self.m_pData.read(_size)
            return _pBuffer
        else:
            # Check if we need to increase capacity
            if (_size + self.m_iSize > self.m_iCapacity):
                self.reserve((_size + self.m_iSize))
            
            # Write the buffer at current position
            self.m_pData.seek(self.m_iSeekPos)
            self.m_pData.write(_pBuffer[:_size])
            
            # Calculate new seek position
            seekpos = self.m_iSeekPos + _size
            
            # Update size if seekpos is beyond current size
            if seekpos >= self.m_iSize:
                self.m_iSize = seekpos
            
            # Update seek position
            self.m_iSeekPos = seekpos
            return _pBuffer

    
    def serialize(self, ptr: Union[int8, uint8, int16, uint16, uint32, int32, float32, float64]) -> None | dtype:
        _dtype = type(ptr)
        if _dtype is bool:
            dtype = uint32
            ptr = uint32(ptr)
        else:
            dtype = _dtype
        size = get_sizeof(ptr)
        format = get_type_format(self.m_byteorder) + get_type_format(dtype)
        buffer = struct.pack(format, ptr)
        buffer = self.serializeInternalBuffer(buffer, size)
        if self.isReading():
            ptr = _dtype(struct.unpack(format, buffer)[0])
        return ptr
        
    
    def serializeBlock8(self, _pBuffer: bytes, _size: uint32):
        _pBuffer = self.serializeInternalBuffer(_pBuffer, _size)
        return _pBuffer
    
    # TODO: Implement ArchiveLinker methods



class ArchiveLinker:
    def __init__(self, archive: ArchiveMemory):
        self.m_pArchive = archive
        self.m_bReading = archive.m_isReading
        self.m_References: dict[int, int] = {}  # Mapping from 32-bit pointers to Python objects (uPtr)

    def get_link(self, ptr: int) -> Optional[Union[int, float, bytes]]:
        # In Python, we just return the reference from the dictionary
        if ptr not in self.m_References:
            return None
        return self.m_References[ptr]
    
    def serialize(self, ptr: Union[int, float, bytes]):
        if self.m_bReading:
            ptr_value = 0
            self.m_pArchive.serialize(ptr_value)
            self.m_References[ptr_value] = ptr
        else:
            ptr_value = ptr & 0xFFFFFFFF  # Simulating 32-bit truncation for 64-bit pointers
            self.m_pArchive.serialize(ptr_value)