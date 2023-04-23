import struct


class RIFF:
    def __init__(self, buffer):
        self.Signature = buffer.read(4)  # Normally RIFF (Resource Interchange File Format)
        if self.Signature != b'RIFF':
            raise TypeError("File is not RIFF!")
        self.FileLength = struct.unpack("I", buffer.read(4))[0]
        self.FileType = buffer.read(4)  # Normally Wave
        self.FormatChunkMarker = buffer.read(4)  # Normally fmt
        formatDataLength = struct.unpack("I", buffer.read(4))[0]
        self.FormatTag = struct.unpack("H", buffer.read(2))[0]  # Waveform-audio format type.
        self.Channels = struct.unpack("H", buffer.read(2))[0]  # Number of channels in the waveform-audio data.
        self.SamplesPerSec = struct.unpack("I", buffer.read(4))[0]  # Sample rate, in samples per second (hertz).
        self.AvgBytesPerSec = struct.unpack("I", buffer.read(4))[0]  # Block alignment, in bytes.
        # The block alignment is the minimum atomic unit of data for the FormatTag format type.
        # (Sample Rate * BitsPerSample * Channels) / 8
        self.BlockAlign = struct.unpack("H", buffer.read(2))[0]
        # (BitsPerSample * Channels) / 8.1 Bytes per Sample Frame
        self.BitsPerSample = struct.unpack("H", buffer.read(2))[0]
        if self.FormatTag == 358:  # XMA2
            self.cbSize = struct.unpack("H", buffer.read(2))[0]  # Size of extra format information.
            self.NumStreams = struct.unpack("H", buffer.read(2))[0]  # Number of audio streams.
            # All streams have two channels, with the exception of the last stream,
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
        elif self.FormatTag == 1:
            buffer.read(4)  # Normally LIST
            # just skip this data we don't use (INFOISFT, Lavf58.76.100)?
            buffer.read(struct.unpack("I", buffer.read(4))[0])

        self.DataChunkMarker = buffer.read(4)  # Normally data
        self.DataLength = struct.unpack("I", buffer.read(4))[0]
        self.Data = buffer.read(self.DataLength)
        self.MetaData = buffer.read()  # unused so just read
        buffer.close()
