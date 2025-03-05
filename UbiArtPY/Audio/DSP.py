import struct

from ..__types__ import uint32, uint16


class DSP:  # WII/GC Format
    """
    Represents a DSP (Digital Signal Processor) audio data structure used in the Wii and GameCube formats.
    This class is primarily used to handle ADPCM-encoded audio data.

    Properties:
        sample_count (uint32): The total number of audio samples in the compressed data.
        adpcm_nibble_count (uint32): The total number of ADPCM nibbles (compressed data units), including frame headers.
        sample_rate (uint32): The sample rate of the audio, in samples per second (e.g., 44100 Hz).
        loop_flag (uint16): Flag indicating whether looping is enabled (1 for enabled, 0 for disabled).
        format_flag (uint16): Format flag, normally always set to 0x00, possibly reserved or unused.
        loop_start (uint32): The byte offset where the loop starts in the audio data.
        loop_end (uint32): The byte offset where the loop ends in the audio data.
        reserved_pointer (uint32): A pointer to the current address, normally always set to 0x00000000.
        coefficients (bytes): A sequence of 8 pairs of coefficients used for the ADPCM decoding process.
        initial_scale (uint16): The initial scale factor used for the first frame's ADPCM decoding.
        initial_sample1 (uint16): The first sample history value used in the initial predictor for the first frame.
        initial_sample2 (uint16): The second sample history value used in the initial predictor for the first frame.
        loop_scale (uint16): The scale factor used for predicting the loop context during looping playback.
        loop_sample1 (uint16): The first sample history value used in the loop context for prediction during looping.
        loop_sample2 (uint16): The second sample history value used in the loop context for prediction during looping.
        data (bytes): The actual compressed ADPCM audio data.

    This class encapsulates the structure required for ADPCM audio playback and manipulation in the
    context of the Wii and GameCube DSP audio formats, including both looping functionality and decoding
    context information.
    """
    sample_count: uint32
    adpcm_nibble_count: uint32  # ADPCM nibble count; includes frame headers
    sample_rate: uint32
    loop_flag: uint16
    format_flag: uint16  # always 0x00
    loop_start: uint32  # Loop start offset
    loop_end: uint32  # Loop end offset
    reserved_pointer: uint32  # Current address; always 0x00000000
    coefficients: bytes  # Coefficient matrix; 8 pairs TODO: make it an object
    initial_scale: uint16  # Initial predictor/scale; always matches first frame headers
    initial_sample1: uint16
    initial_sample2: uint16
    loop_scale: uint16  # Loop context predictor/scale
    loop_sample1: uint16
    loop_sample2: uint16
    data: bytes  # ADPCM Data

    # TODO: implement ArchiveMemory
    def __init__(self, buffer):
        self.sample_count = struct.unpack(">I", buffer.read(4))[0]
        self.adpcm_nibble_count = struct.unpack(">I", buffer.read(4))[0]
        self.sample_rate = struct.unpack(">I", buffer.read(4))[0]
        self.loop_flag = struct.unpack(">H", buffer.read(2))[0]
        self.format_flag = struct.unpack(">H", buffer.read(2))[0]
        self.loop_start = struct.unpack(">I", buffer.read(4))[0]
        self.loop_end = struct.unpack(">I", buffer.read(4))[0]
        self.reserved_pointer = struct.unpack(">I", buffer.read(4))[0]
        self.coefficients = buffer.read(32)
        self.Gain = struct.unpack(">H", buffer.read(2))[0]
        self.initial_scale = struct.unpack(">H", buffer.read(2))[0]
        self.initial_sample1 = struct.unpack(">H", buffer.read(2))[0]
        self.initial_sample2 = struct.unpack(">H", buffer.read(2))[0]
        self.loop_scale = struct.unpack(">H", buffer.read(2))[0]
        self.loop_sample1 = struct.unpack(">H", buffer.read(2))[0]
        self.loop_sample2 = struct.unpack(">H", buffer.read(2))[0]
        buffer.seek(0x16, 1)  # Reserved
        self.data = buffer.read()
        buffer.close()
