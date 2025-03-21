import zlib

from djangoredis.compressors.base import BaseCompressor
from djangoredis.exceptions import CompressorError


class ZlibCompressor(BaseCompressor):
    min_length = 15
    preset = 6

    def compress(self, value: bytes) -> bytes:
        if len(value) > self.min_length:
            return zlib.compress(value, self.preset)
        return value

    def decompress(self, value: bytes) -> bytes:
        try:
            return zlib.decompress(value)
        except zlib.error as e:
            raise CompressorError from e
