import struct

from ..__types__ import uint32, uint16
from ..__utils__ import InvalidFileError


class RIFF:
    signature: bytes
    file_length: uint32
    file_type: bytes
    format_chunk_marker: bytes
    format_tag: uint16
    channels: uint16
    samples_per_sec: uint32
    avg_bytes_per_sec: uint32
    block_align: uint16
    bits_per_sample: uint16

    def __init__(self, buffer):
        self.signature = buffer.read(4)  # Normally RIFF (Resource Interchange File Format)
        if self.signature != b'RIFF':
            raise InvalidFileError("Invalid file! File is not a RIFF!")
        self.file_length = struct.unpack("I", buffer.read(4))[0]
        self.file_type = buffer.read(4)  # Normally Wave
        self.format_chunk_marker = buffer.read(4)  # Normally fmt
        format_data_length = struct.unpack("I", buffer.read(4))[0]
        self.format_tag = struct.unpack("H", buffer.read(2))[0]  # Waveform-audio format type.
        self.channels = struct.unpack("H", buffer.read(2))[0]  # Number of channels in the waveform-audio data.
        self.samples_per_sec = struct.unpack("I", buffer.read(4))[0]  # Sample rate, in samples per second (hertz).
        self.avg_bytes_per_sec = struct.unpack("I", buffer.read(4))[0]  # Block alignment, in bytes.
        # The block alignment is the minimum atomic unit of data for the FormatTag format type.
        # (Sample Rate * BitsPerSample * Channels) / 8
        self.block_align = struct.unpack("H", buffer.read(2))[0]
        # (BitsPerSample * Channels) / 8.1 Bytes per Sample Frame
        self.bits_per_sample = struct.unpack("H", buffer.read(2))[0]
        if self.format_tag == 358:  # XMA2
            self.cbSize = struct.unpack("H", buffer.read(2))[0]  # Size of extra format information.
            self.NumStreams = struct.unpack("H", buffer.read(2))[0]  # Number of audio streams.
            # All streams have two channels, except the last stream,
            # which has one channel if the source file's total channel count is odd.
            self.ChannelMask = struct.unpack("I", buffer.read(4))[0]  # Spatial positions of the channels in this file.
            self.SamplesEncoded = struct.unpack("I", buffer.read(4))[0]
            # Total number of PCM samples to which the file decodes.
            buffer.read(1)  # idk?
            self.BytesPerBlock = struct.unpack("H", buffer.read(2))[0]  # XMA block size.
            self.EncodeOptions = struct.unpack("B", buffer.read(1))[0]  # Not Sure
            self.PlayBegin = struct.unpack("I", buffer.read(4))[0]  # First valid sample in the decoded audio.
            self.PlayLength = struct.unpack("I", buffer.read(4))[0]
            # Length of the valid part of the decoded audio.
            self.LoopBegin = struct.unpack("I", buffer.read(4))[0]
            # Beginning of the loop region in decoded sample terms.
            self.LoopLength = struct.unpack("I", buffer.read(4))[0]
            # Length of the loop region in decoded sample terms.
            self.LoopCount = struct.unpack("B", buffer.read(1))[0]
            # Number of times to loop. A 0 indicates no looping, while 255 indicates infinite looping.
            self.EncoderVersion = struct.unpack("B", buffer.read(1))[0]
            # Version of XMA encoder that generated the file.
            self.BlockCount = struct.unpack("H", buffer.read(2))[0]
            # XMA blocks in file (and entries in its seek table).
            self.SeekChunkMarker = buffer.read(4)
            self.seekTableLength = struct.unpack("I", buffer.read(4))[0]
            self.SeekTable = buffer.read(self.seekTableLength)
        elif self.format_tag == 1:
            buffer.read(4)  # Normally LIST
            # just skip this data we don't use (INFOISFT, Lavf58.76.100)?
            buffer.read(struct.unpack("I", buffer.read(4))[0])

        self.DataChunkMarker = buffer.read(4)  # Normally data
        self.DataLength = struct.unpack("I", buffer.read(4))[0]
        self.Data = buffer.read(self.DataLength)
        self.MetaData = buffer.read()  # unused so just read
        buffer.close()
