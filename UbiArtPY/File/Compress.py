from ..__types__ import Path, uint32
import zlib
import lzma


class Compress:
    COMPRESSION_SIZE = 32768

    @staticmethod
    def get_max_chunk_size() -> int:
        return Compress.COMPRESSION_SIZE

    @staticmethod
    def compute_size_required(source_size) -> uint32:
        # Upon entry, destLen is the total size of the destination buffer,
        # which must be at least 0.1% larger than sourceLen plus 12 bytes
        target_size = uint32(source_size * 1.1 + 12 + 1)  # +1 roundup
        return target_size

    @staticmethod
    def uncompress_file(src_filename: Path, dst_filename: Path) -> bool:
        with open(src_filename, "rb") as read_file:
            filesize = read_file.seek(0, 2)
            read_file.seek(0) # return to 0
            with open(dst_filename, "wb") as write_file:
                target_size = Compress.compute_size_required(Compress.COMPRESSION_SIZE)
                destination = bytearray(target_size)
                source = bytearray(Compress.COMPRESSION_SIZE)

                bytes_remaining = filesize

                while bytes_remaining != 0:
                    compressed_size = int.from_bytes(read_file.read(4), "little")
                    bytes_remaining -= 4

                    source[:compressed_size] = read_file.read(compressed_size)
                    if compressed_size != 0:
                        decompressed_data = Compress.uncompress_buffer(
                            destination, target_size, source[:compressed_size]
                        )

                    bytes_remaining -= compressed_size

                    write_file.write(decompressed_data)

        return True

    # compress in our own format, external zip are not supported
    @staticmethod
    def compress_file(src_filename: Path, dst_filename: Path) -> bool:
        with open(src_filename, "rb") as read_file:
            filesize = read_file.seek(0, 2)
            read_file.seek(0) # return to 0
            with open(dst_filename, "wb") as write_file:
                target_size = Compress.compute_size_required(Compress.COMPRESSION_SIZE)
                destination = bytearray(target_size)
                source = bytearray(Compress.COMPRESSION_SIZE)

                bytes_remaining = filesize

                while bytes_remaining != 0:
                    bytes_to_read = min(bytes_remaining, Compress.COMPRESSION_SIZE)
                    source[:bytes_to_read] = read_file.read(bytes_to_read)

                    compressed_data = Compress.compress_buffer(
                        destination, target_size, source[:bytes_to_read]
                    )
                    compressed_size = len(compressed_data)

                    write_file.write(compressed_size.to_bytes(4, "little"))
                    write_file.write(compressed_data)

                    bytes_remaining -= bytes_to_read

        return True

    @staticmethod
    def compress_buffer_zlib(source) -> bytes:
        try:
            compressed_data = zlib.compress(source)
            return compressed_data
        except MemoryError:
            raise MemoryError("Not enough memory to compress")
        except BufferError as e:
            raise e
    
    @staticmethod
    def compress_buffer_lzma(source) -> bytes:
        try:
            compressed_data = lzma.compress(source)
            return compressed_data
        except MemoryError:
            raise MemoryError("Not enough memory to compress")
        except BufferError as e:
            raise e

    @staticmethod
    def uncompress_buffer_zlib(source) -> bytes:
        decompressed_data = zlib.decompress(source)
        return decompressed_data

    @staticmethod
    def uncompress_buffer_lzma(source) -> bytes:
        decompressed_data = lzma.decompress(source)
        return decompressed_data
    
    @staticmethod
    def parse_gzip_buffer(source):
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
