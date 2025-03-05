import lzma
import zlib

from ..__types__ import uint32


class Compress:
    COMPRESSION_SIZE = 32768

    @staticmethod
    def get_max_chunk_size() -> int:
        return Compress.COMPRESSION_SIZE

    @staticmethod
    def compute_size_required(source_size: float) -> uint32:
        # Upon entry, destLen is the total size of the destination buffer,
        # which must be at least 0.1% larger than sourceLen plus 12 bytes
        target_size = uint32(source_size * 1.1 + 12 + 1)  # +1 roundup
        return target_size

    @staticmethod
    def compress_buffer_zlib(source: bytes) -> bytes:
        try:
            compressed_data = zlib.compress(source)
            return compressed_data
        except MemoryError:
            raise MemoryError("Not enough memory to compress")
        except BufferError as e:
            raise e

    @staticmethod
    def compress_buffer_lzma(source: bytes) -> bytes:
        try:
            compressed_data = lzma.compress(source)
            return compressed_data
        except MemoryError:
            raise MemoryError("Not enough memory to compress")
        except BufferError as e:
            raise e

    @staticmethod
    def uncompress_buffer_zlib(source: bytes) -> bytes:
        decompressed_data = zlib.decompress(source)
        return decompressed_data

    @staticmethod
    def uncompress_buffer_lzma(source: bytes) -> bytes:
        decompressed_data = lzma.decompress(source)
        return decompressed_data

    @staticmethod
    def parse_gzip_buffer(source: bytes):
        header_size = 10
        footer_size = 8  # 2 * sizeof(u32)
        if len(source) < header_size + footer_size:
            raise ValueError("Compressed size is too small")

        if source[:2] != b'\x1f\x8b':
            raise ValueError("Invalid GZIP magic numbers")

        compression_method = source[2]
        if compression_method != 8:  # Z_DEFLATED
            raise ValueError("Unknown compression method")

        flags = source[3]
        if flags & 0x08:  # FLAG_ORIG_NAME
            start = header_size
            while source[start] != 0:
                start += 1
            start += 1
        else:
            start = header_size

        compressed_data = source[start:-footer_size]
        footer = source[-footer_size:]

        target_crc32 = int.from_bytes(footer[:4], "little")
        target_size = int.from_bytes(footer[4:], "little")

        return compressed_data, target_size, target_crc32
