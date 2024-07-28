import struct
from ..__utils__ import InvalidFileError

# Constants for the format and chunk types
RIFF_SIGNATURE = b'RIFF'
WAVE_TYPE = b'WAVE'
FMT_CHUNK = b'fmt '
DATA_CHUNK = b'data'
LIST_CHUNK = b'LIST'
INFO_TYPE = b'INFO'
XMA2_FORMAT = 358
PCM_FORMAT = 1

class RIFF:
    """Class to handle RIFF (WAVE) files and extract metadata and audio data."""

    def __init__(self, buffer):
        """Initialize and parse a RIFF file from a given buffer."""
        self._parse_file(buffer)

    @staticmethod
    def from_file(filepath):
        """Initialize a RIFF object with a given file."""
        with open(filepath, 'rb') as file:
            return RIFF(file)
    
    def _parse_file(self, buffer):
        """Parse the RIFF file from the provided buffer."""
        self._validate_signature(buffer)
        self._read_chunks(buffer)
        self.MetaData = buffer.read()  # Unused data, just read
        buffer.close()

    def _validate_signature(self, buffer):
        """Validate the RIFF file signature and type."""
        self.Signature = buffer.read(4)
        if self.Signature != RIFF_SIGNATURE:
            raise InvalidFileError("Invalid file! File is not a RIFF!")
        self.FileLength = struct.unpack("<I", buffer.read(4))[0]
        self.FileType = buffer.read(4)
        if self.FileType != WAVE_TYPE:
            raise InvalidFileError("Invalid file! File is not a WAVE file!")

    def _read_chunks(self, buffer):
        """Read all chunks from the RIFF file."""
        self.metadata = {}
        while True:
            chunk_id = buffer.read(4)
            if not chunk_id:
                break

            chunk_size = struct.unpack("<I", buffer.read(4))[0]
            if chunk_id == FMT_CHUNK:
                self._read_fmt_chunk(buffer, chunk_size)
            elif chunk_id == DATA_CHUNK:
                self._read_data_chunk(buffer, chunk_size)
            elif chunk_id == LIST_CHUNK:
                self._read_list_chunk(buffer, chunk_size)
            else:
                buffer.read(chunk_size)  # Skip unknown chunks

    def _read_fmt_chunk(self, buffer, chunk_size):
        """Read the fmt chunk and extract format information."""
        self.FormatTag = struct.unpack("<H", buffer.read(2))[0]
        self.Channels = struct.unpack("<H", buffer.read(2))[0]
        self.SamplesPerSec = struct.unpack("<I", buffer.read(4))[0]
        self.AvgBytesPerSec = struct.unpack("<I", buffer.read(4))[0]
        self.BlockAlign = struct.unpack("<H", buffer.read(2))[0]
        self.BitsPerSample = struct.unpack("<H", buffer.read(2))[0]

        if self.FormatTag == XMA2_FORMAT:
            self._read_xma2_format(buffer)
        elif self.FormatTag == PCM_FORMAT:
            buffer.read(4)  # Normally LIST, skip this unused part
            buffer.read(struct.unpack("<I", buffer.read(4))[0])
        else:
            buffer.read(chunk_size - 16)  # Skip remaining bytes in the fmt chunk

    def _read_xma2_format(self, buffer):
        """Read the fields specific to the XMA2 format."""
        self.cbSize = struct.unpack("<H", buffer.read(2))[0]
        self.NumStreams = struct.unpack("<H", buffer.read(2))[0]
        self.ChannelMask = struct.unpack("<I", buffer.read(4))[0]
        self.SamplesEncoded = struct.unpack("<I", buffer.read(4))[0]
        self.EncodeOptions = struct.unpack("<B", buffer.read(1))[0]
        self.BytesPerBlock = struct.unpack("<H", buffer.read(2))[0]
        self.EncodeOptions = struct.unpack("<B", buffer.read(1))[0]
        self.PlayBegin = struct.unpack("<I", buffer.read(4))[0]
        self.PlayLength = struct.unpack("<I", buffer.read(4))[0]
        self.LoopBegin = struct.unpack("<I", buffer.read(4))[0]
        self.LoopLength = struct.unpack("<I", buffer.read(4))[0]
        self.LoopCount = struct.unpack("<B", buffer.read(1))[0]
        self.EncoderVersion = struct.unpack("<B", buffer.read(1))[0]
        self.BlockCount = struct.unpack("<H", buffer.read(2))[0]
        self.SeekChunkMarker = buffer.read(4)
        self.seekTableLength = struct.unpack("<I", buffer.read(4))[0]
        self.SeekTable = buffer.read(self.seekTableLength)

    def _read_data_chunk(self, buffer, chunk_size):
        """Read the audio data chunk."""
        self.DataChunkMarker = DATA_CHUNK
        self.DataLength = chunk_size
        self.Data = buffer.read(self.DataLength)

    def _read_list_chunk(self, buffer, chunk_size):
        """Read the LIST chunk and extract metadata if present."""
        list_type = buffer.read(4)
        if list_type == INFO_TYPE:
            self._read_info_chunk(buffer, chunk_size - 4)
        else:
            buffer.read(chunk_size - 4)  # Skip unknown LIST chunk

    def _read_info_chunk(self, buffer, size):
        """Read subchunks within an INFO chunk and extract metadata."""
        end_position = buffer.tell() + size
        while buffer.tell() < end_position:
            info_chunk_id = buffer.read(4)
            info_chunk_size = struct.unpack("<I", buffer.read(4))[0]
            info_data = buffer.read(info_chunk_size).decode('ascii').rstrip('\0')
            self.metadata[info_chunk_id.decode('ascii')] = info_data
