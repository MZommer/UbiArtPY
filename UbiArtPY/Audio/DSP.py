import struct


class DSP:  # WII/GC Format
    def __init__(self, buffer):
        self.SampleCount = struct.unpack(">I", buffer.read(4))[0]  # Sample count
        self.NibbleCount = struct.unpack(">I", buffer.read(4))[0]  # ADPCM nibble count; includes frame headers
        self.SampleRate = struct.unpack(">I", buffer.read(4))[0]  # Sample rate
        self.Loop = struct.unpack(">H", buffer.read(2))[0]  # Loop flag
        self.Format = struct.unpack(">H", buffer.read(2))[0]  # Format flag; always 0x00
        self.LoopStart = struct.unpack(">I", buffer.read(4))[0]  # Loop start offset
        self.LoopEnd = struct.unpack(">I", buffer.read(4))[0]  # Loop end offset
        self.Pointer = struct.unpack(">I", buffer.read(4))[0]  # Current address; always 0x00
        self.Coefficients = buffer.read(32)  # Coefficient matrix; 8 pairs
        self.Gain = struct.unpack(">H", buffer.read(2))[0]
        self.InitialScale = struct.unpack(">H", buffer.read(2))[0]
        # Initial predictor/scale; always matches first frame headers
        self.InitialSample1 = struct.unpack(">H", buffer.read(2))[0]  # Initial sample history 1
        self.InitialSample2 = struct.unpack(">H", buffer.read(2))[0]  # Initial sample history 2
        self.LoopScale = struct.unpack(">H", buffer.read(2))[0]  # Loop context predictor/scale
        self.LoopSample1 = struct.unpack(">H", buffer.read(2))[0]  # Loop context sample history 1
        self.LoopSample2 = struct.unpack(">H", buffer.read(2))[0]  # Loop context sample history 2
        buffer.seek(0x16, 1)  # Reserved
        self.Data = buffer.read()  # ADPCM Data
        buffer.close()
