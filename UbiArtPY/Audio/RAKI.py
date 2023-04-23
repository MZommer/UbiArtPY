import os
from datetime import timedelta
from math import ceil
from ..__utils__ import system, useTemp, InvalidFileError
from .DSP import *
from .RIFF import *


class RAKI:
    Version: int
    Platform: str
    Format: bytes
    HeaderLenght: int
    DataOffset: int
    NumberOfChunks: int
    unk: int

    isAMB: bool
    Endianess: str

    def __init__(self,
                 Version=10,
                 Platform="ELOT",
                 Format="PCM ",
                 HeaderLenght=32,
                 DataOffset=32,
                 NumberOfChunks=0,
                 unk=0):
        self.Version = Version
        self.Platform = Platform
        self.Format = Format
        self.HeaderLength = HeaderLenght
        self.DataOffset = DataOffset
        self.NumberOfChunks = NumberOfChunks
        self.unk = unk

    @staticmethod
    def SyncJDUAudio(file, output, startBeat, markers, amboutput=None) -> bool:
        """Synchronizes the audio with the beat, returns true if amb is generated"""
        # TODO: check if getting the videooffset its not the same
        delay = round(markers[abs(startBeat)] / 48)
        if startBeat == 0:
            system(f'ffmpeg -i {file} -af "volume=2.8" {output}')
        elif startBeat > 0:  # Delays
            system(f'ffmpeg -i {file} -af "adelay={delay}:all=true:volume=2.8" {output}')
        else:  # Cuts
            timestamp = timedelta(seconds=delay / 1000)
            system(f'ffmpeg -ss {timestamp} -i {file} -af "volume=2.8" {output}')
            if amboutput:
                system(f'ffmpeg -t {timestamp} -i {file} -af "volume=2.8" {amboutput}')
                return True

    @staticmethod
    def getPlatform(platform: str) -> bytes:
        return {
            "PC": b"Win ",
            "X360": b"X360",
            "PS3": b"PS3 ",
            "ORBIS": b"Orbi",
            "WII": b"Wii ",
            "WIIU": b"Cafe",
            "CAFE": b"Cafe",
            "DURANGO": b"Dura",
            "XONE": b"Dura",
            "NX": b"Nx  ",
        }[platform]

    @staticmethod
    def getVersion(platform: str) -> int:
        return {
            "PC": 10,
            "WIIU": 8,
            "CAFE": 8,
            "NX": 11,
            "WII": 8,
            "ORBIS": 9,
            "PS3": 9,
            "X360": 8
        }[platform]

    @staticmethod
    def getFormat(platform: str, isAmb: bool) -> bytes:
        if isAmb:
            return {
                "PC": b"pcm ",
                "WIIU": b"adpc",
                "CAFE": b"adpc",
                "NX": b"pcm ",
                "WII": b"adpc",
                "ORBIS": b"pcm ",
                "PS3": b"mp3 ",
                "X360": B"xma2"
            }[platform]
        else:
            return {
                "PC": b"pcm ",
                "WIIU": b"adpc",
                "CAFE": b"adpc",
                "NX": b"Nx  ",
                "WII": b"adpc",
                "ORBIS": b"pcm ",
                "PS3": b"mp3 ",
                "X360": B"xma2"
            }[platform]

    @staticmethod
    def getEndianess(fmt: bytes) -> str:
        return {
            b"pcm ": "LITTLE",
            b"adpc": "BIG",
            b"Nx  ": "LITTLE",
            b"mp3 ": "BIG",
            b"xma2": "BIG",
            b"msadpcm": "LITTLE",
        }[fmt]

    def __CookRAKIHeader(self, buffer):
        self.RAKIHeaderLength = 0x20
        byteOrder = ">" if self.Endianess.upper() == "BIG" else "<"
        buffer.write(b"RAKI")  # RAKI signature
        buffer.write(struct.pack(byteOrder + "I", self.Version))
        buffer.write(self.Platform)
        buffer.write(self.Format)
        buffer.write(struct.pack(byteOrder + "I", self.HeaderLength))
        buffer.write(struct.pack(byteOrder + "I", self.DataOffset))
        buffer.write(struct.pack(byteOrder + "I", self.NumberOfChunks))
        buffer.write(struct.pack(byteOrder + "I", self.unk))

    def __CookNX(self, raki):
        self.HeaderLength = 0x58
        self.DataOffset = 0x58
        self.NumberOfChunks = 3
        self.__CookRAKIHeader(raki)
        wave = RIFF(open("/temp/temp.wav", "rb"))
        system('OpusEncoder --bitrate 192000  -o \\temp\\temp.lopus \\temp\\temp.wav')
        with open("\\temp\\temp.lopus", "rb") as opus:
            data = opus.read()
            dataSize = opus.tell()

        raki.write(wave.FormatChunkMarker)
        raki.write(struct.pack("I", 68))  # Chunk Offset
        raki.write(struct.pack("I", 16))  # Chunk Length

        raki.write(b"AdIn")
        raki.write(struct.pack("I", 84))  # Chunk Offset
        raki.write(struct.pack("I", 4))  # Chunk Length

        raki.write(wave.DataChunkMarker)
        raki.write(struct.pack("I", 88))  # Chunk Offset
        raki.write(struct.pack("I", dataSize))  # Data Length

        raki.write(struct.pack("H", 0x63))
        raki.write(struct.pack("H", wave.Channels))
        raki.write(struct.pack("I", wave.SamplesPerSec))
        raki.write(struct.pack("I", wave.AvgBytesPerSec))
        raki.write(struct.pack("H", wave.BlockAlign))
        raki.write(struct.pack("H", wave.BitsPerSample))
        raki.write(struct.pack("I",
                               int(wave.DataLength / (wave.Channels * wave.BitsPerSample / 8))))
        # Gets the number of samples

        raki.write(data)

        os.remove("/temp/temp.lopus")

    def __CookPCM(self, raki):
        self.HeaderLength = 72
        self.DataOffset = 72
        self.NumberOfChunks = 2
        # Hard codded
        self.__CookRAKIHeader(raki)
        wave = RIFF(open("/temp/temp.wav", "rb"))
        raki.write(wave.FormatChunkMarker)
        raki.write(struct.pack("I", 56))  # Chunk Offset
        raki.write(struct.pack("I", 12))  # Chunk Length

        raki.write(wave.DataChunkMarker)
        raki.write(struct.pack("I", 72))  # Chunk Offset
        raki.write(struct.pack("I", wave.DataLength))  # Data Length

        raki.write(struct.pack("H", wave.FormatTag))
        raki.write(struct.pack("H", wave.Channels))
        raki.write(struct.pack("I", wave.SamplesPerSec))
        raki.write(struct.pack("I", wave.AvgBytesPerSec))
        raki.write(struct.pack("H", wave.BlockAlign))
        raki.write(struct.pack("H", wave.BitsPerSample))

        raki.write(wave.Data)

    def __CookMP3(self, raki):
        # TODO: update so it takes the data from the mp3, not the wave
        self.HeaderLength = 0x48
        self.DataOffset = 0x80
        self.NumberOfChunks = 2
        # Hard codded
        self.__CookRAKIHeader(raki)
        wave = RIFF(open("/temp/temp.wav", "rb"))
        system('ffmpeg -i \\temp\\temp.wav -write_xing 0 -id3v2_version 0 -b:a 192k -ac 2 -ar 48000 \\temp\\temp.mp3')
        with open("\\temp\\temp.mp3", "rb") as mp3:
            data = mp3.read()

        raki.write(b"fmt ")
        raki.write(struct.pack(">I", 56))  # Chunk Offset
        raki.write(struct.pack(">I", 16))  # Chunk Length

        raki.write(b"Msf ")
        raki.write(struct.pack(">I", self.DataOffset))  # Data Offset
        raki.write(struct.pack(">I", len(data)))  # Data Length

        raki.write(struct.pack(">H", 0x55))  # Format flag hardcoded
        raki.write(struct.pack(">H", wave.Channels))
        raki.write(struct.pack(">I", wave.SamplesPerSec))
        raki.write(struct.pack(">I", wave.AvgBytesPerSec))
        raki.write(struct.pack(">H", wave.BlockAlign))
        raki.write(struct.pack(">H", wave.BitsPerSample))
        raki.write(b"\x00" * 56)
        # spacing? if deleted the game will not read it properly

        raki.write(data)

        os.remove("/temp/temp.mp3")

    def __CookXMA2(self, raki):
        system(r'xma2encode \temp\temp.wav /BlockSize 4 /Quality 92 /TargetFile \temp\temp.xma')
        xma2 = RIFF(open("/temp/temp.xma", "rb"))

        dataOffset = 120 + xma2.seekTableLength
        dataOffsetSpaced = ceil(dataOffset / 2048) * 2048
        spacing = dataOffsetSpaced - dataOffset
        self.HeaderLength = dataOffset
        self.DataOffset = dataOffsetSpaced
        self.NumberOfChunks = 3
        # Hard codded
        self.__CookRAKIHeader(raki)

        raki.write(xma2.FormatChunkMarker)
        raki.write(struct.pack(">I", 68))  # Chunk Offset
        raki.write(struct.pack(">I", 52))  # Chunk Length

        raki.write(xma2.SeekChunkMarker)
        raki.write(struct.pack(">I", 120))  # Chunk Offset
        raki.write(struct.pack(">I", xma2.seekTableLength))

        raki.write(xma2.DataChunkMarker)
        raki.write(struct.pack(">I", dataOffsetSpaced))  # Chunk Offset
        raki.write(struct.pack(">I", xma2.DataLength))  # Data Length
        raki.write(struct.pack(">H", xma2.FormatTag))
        raki.write(struct.pack(">H", xma2.Channels))
        raki.write(struct.pack(">I", xma2.SamplesPerSec))
        raki.write(struct.pack(">I", xma2.AvgBytesPerSec))
        raki.write(struct.pack(">H", xma2.BlockAlign))
        raki.write(struct.pack(">H", xma2.BitsPerSample))
        raki.write(struct.pack(">H", xma2.cbSize))
        raki.write(struct.pack(">H", xma2.NumStreams))
        raki.write(struct.pack(">I", xma2.ChannelMask))
        raki.write(struct.pack(">I", xma2.SamplesEncoded))
        raki.write(struct.pack(">I", 4096))  # absolutely no idea where this come from
        raki.write(struct.pack(">I", xma2.PlayBegin))
        raki.write(struct.pack(">I", xma2.PlayLength))
        raki.write(struct.pack(">I", xma2.LoopBegin))
        raki.write(struct.pack(">I", xma2.LoopLength))
        raki.write(struct.pack(">B", xma2.LoopCount))
        raki.write(struct.pack(">B", xma2.EncoderVersion))
        raki.write(struct.pack(">H", xma2.BlockCount))

        raki.write(xma2.SeekTable)
        raki.write(b"\x00" * spacing)
        raki.write(xma2.Data)

        os.remove("/temp/temp.xma")

    def __CookDSP(self, raki):
        # TODO: finish? missing the writing data
        # Split in channels
        system("ffmpeg -i \\temp\\temp.wav -ar 32000 -map_channel 0.0.0 \\temp\\left.wav "
               "-ar 32000 -map_channel 0.0.1 \\temp\\right.wav")
        # Convert to dsp every channel
        system('DSPADPCM -E \\temp\\left.wav \\temp\\left.dsp')
        system('DSPADPCM -E \\temp\\right.wav \\temp\\right.dsp')
        dsp_left = DSP(open("\\temp\\left.dsp", "rb"))
        dsp_right = DSP(open("\\temp\\right.dsp", "rb"))
        wav_left = RIFF(open("\\temp\\left.wav", "rb"))
        # wav_right = RIFF(open("\\temp\\right.wav", "rb"))

        if self.isAMB:
            self.HeaderLength = 0x12E
            self.NumberOfChunks = 5
        else:
            self.HeaderLength = 0x122
            self.NumberOfChunks = 4

        self.DataOffset = 0x140
        # Hard codded
        self.__CookRAKIHeader(raki)
        # Chunks
        print("Writting chunks data?")
        raki.write(b"fmt ")
        raki.write(struct.pack(">I", 0x5C if self.isAMB else 0x50))  # FMT chunk offset
        raki.write(struct.pack(">I", 0x12))  # FMT chunk size
        if self.isAMB:
            raki.write(b"dspL")
            raki.write(struct.pack(">I", 0x6E))  # dspL chunk offset
            raki.write(struct.pack(">I", 0x60))  # dspL chunk size
            raki.write(b"dspR")
            raki.write(struct.pack(">I", 0xCE))  # dspR chunk offset
            raki.write(struct.pack(">I", 0x60))  # dspR chunk size
            raki.write(b"datL")
            raki.write(struct.pack(">I", 0x140))  # datL chunk offset
            raki.write(struct.pack(">I", len(dsp_left.Data)))  # datL chunk size
            raki.write(b"datR")
            raki.write(struct.pack(">I", 0x140 + len(dsp_left.Data) + 0x10))  # datR chunk offset
            raki.write(struct.pack(">I", len(dsp_right.Data)))  # datR chunk size
        else:
            raki.write(b"dspL")
            raki.write(struct.pack(">I", 0x62))  # dspL chunk offset
            raki.write(struct.pack(">I", 0x60))  # dspL chunk size
            raki.write(b"dspR")
            raki.write(struct.pack(">I", 0xC2))  # dspR chunk offset
            raki.write(struct.pack(">I", 0x60))  # dspR chunk size
            raki.write(b"datS")
            raki.write(struct.pack(">I", 0x140))  # datS chunk offset
            raki.write(struct.pack(">I", len(dsp_left.Data) + len(dsp_right.Data)))  # datS chunk size

        # Data
        # fmt data
        raki.write(struct.pack(">H", 2))  # format
        raki.write(struct.pack(">H", 2))  # channels
        raki.write(struct.pack(">I", wav_left.BitsPerSample))  # frequency
        raki.write(struct.pack(">I", int(wav_left.BitsPerSample * 2 * 16 / 16)))  # byterate
        raki.write(struct.pack(">H", int(2 * 16 / 16)))  # blockalign
        raki.write(struct.pack(">H", 16))  # bitspersample
        raki.write(struct.pack(">H", 0))  # padding
        # left coeff
        raki.write(dsp_left.Coefficients)
        # right coeff
        raki.write(dsp_right.Coefficients)
        # padding
        raki.write(b"\x00" * 30)

    @useTemp
    def Cook(self, file, output, platform, isAMB=False, Format=None):
        platform = platform.upper()
        self.isAMB = isAMB
        file = os.path.abspath(file)
        output = os.path.abspath(output)
        self.Version = self.getVersion(platform)
        self.Platform = self.getPlatform(platform)
        self.unk = self.unk or (0 if self.isAMB else 3)
        self.Format = Format or self.getFormat(platform, self.isAMB)
        self.Endianess = self.getEndianess(self.Format)

        system(f'ffmpeg -y -i "{file}" -vn -map_metadata -1 \\temp\\temp.wav')
        file = os.path.abspath("temp\\temp.wav")
        with open(output, "wb") as raki:
            if self.Format == b"pcm ":
                self.__CookPCM(raki)
            elif self.Format == b"Nx  ":
                self.__CookNX(raki)
            elif self.Format == b"mp3 ":
                self.__CookMP3(raki)
            elif self.Format == b"xma2":
                self.__CookXMA2(raki)
            elif self.Format == b"adpc":
                self.__CookDSP(raki)  # Format is "adpc" cause the dsp data is in adpcm
            elif self.Format == b"msadpcm":
                self.__CookMSADPCM(raki)
        os.remove("/temp/temp.wav")

    @staticmethod
    def Parse(path):
        """
        TODO: Add parsing for the format chunks
              Add endianess for each platform?
        """
        self = RAKI()
        with open(path, "rb") as ckd:
            Signature = ckd.read(4)
            if Signature == b"RAKI":
                raise InvalidFileError("Invalid RAKI file!")
            self.Version = struct.unpack(">I", ckd.read(4))[0]
            self.Platform = ckd.read(4)
            self.Format = ckd.read(4)
            self.HeaderLength = struct.unpack(">I", ckd.read(4))[0]
            self.DataOffset = struct.unpack(">I", ckd.read(4))[0]
            self.NumberOfChunks = struct.unpack(">I", ckd.read(4))[0]
            self.unk = struct.unpack(">I", ckd.read(4))[0]
        return self

    @staticmethod
    def UnCook(file, output):
        system(f'vgmstream -o {output} {file}')

    @staticmethod
    @useTemp
    def UnCookAndCook(file, output, platform):
        RAKI.UnCook(file, "/temp/uncooktemp.wav")
        inRAKI = RAKI.Parse(file)
        outRAKI = RAKI()
        outRAKI.unk = inRAKI.unk
        outRAKI.Cook("/temp/uncooktemp.wav", output, platform)
        os.remove("/temp/uncooktemp.wav")
