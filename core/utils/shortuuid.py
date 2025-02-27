import binascii
import logging
import math
import os
import uuid as _uu

from typing import List, Optional

logger = logging.getLogger(__name__)


def int_to_string(number: int, alphabet: List[str], padding: Optional[int] = None) -> str:
    output = ''
    alpha_len = len(alphabet)
    while number:
        number, digit = divmod(number, alpha_len)
        output += alphabet[digit]
    if padding:
        remainder = max(padding - len(output), 0)
        output = output + alphabet[0] * remainder
    return output[::-1]


def string_to_int(string: str, alphabet: List[str]) -> int:
    number = 0
    alpha_len = len(alphabet)
    for char in string:
        number = number * alpha_len + alphabet.index(char)
    return number


class ShortUUID(object):
    def __init__(self, alphabet: Optional[List[str]] = None) -> None:
        if alphabet is None:
            alphabet = list(
                '23456789ABCDEFGHJKLMNPQRSTUVWXYZ' 'abcdefghijkmnopqrstuvwxyz'
            )
        self.set_alphabet(alphabet)

    @property
    def _length(self) -> int:
        return int(math.ceil(math.log(2 ** 128, self._alpha_len)))

    def encode(self, uuid: _uu.UUID, pad_length: Optional[int] = None) -> str:
        if not isinstance(uuid, _uu.UUID):
            raise ValueError('Input `uuid` must be a UUID object.')
        if pad_length is None:
            pad_length = self._length
        return int_to_string(uuid.int, self._alphabet, padding=pad_length)

    def decode(self, string: str, legacy: bool = False) -> _uu.UUID:
        if not isinstance(string, str):
            raise ValueError('Input `string` must be a str.')
        if legacy:
            string = string[::-1]
        return _uu.UUID(int=string_to_int(string, self._alphabet))

    def uuid(self, name: Optional[str] = None, pad_length: Optional[int] = None) -> str:
        if pad_length is None:
            pad_length = self._length
        if name is None:
            value = _uu.uuid4()
        elif name.lower().startswith(('http://', 'https://')):
            value = _uu.uuid5(_uu.NAMESPACE_URL, name)
        else:
            value = _uu.uuid5(_uu.NAMESPACE_DNS, name)
        return self.encode(value, pad_length)

    def random(self, length: Optional[int] = None) -> str:
        if length is None:
            length = self._length
        random_num = int(binascii.b2a_hex(os.urandom(length)), 16)
        return int_to_string(random_num, self._alphabet, padding=length)[:length]

    def get_alphabet(self) -> str:
        return ''.join(self._alphabet)

    def set_alphabet(self, alphabet: str) -> None:
        new_alphabet = list(sorted(set(alphabet)))
        if len(new_alphabet) > 1:
            self._alphabet = new_alphabet
            self._alpha_len = len(self._alphabet)
        else:
            raise ValueError('Alphabet with more than ' 'one unique symbols required.')

    def encoded_length(self, num_bytes: int = 16) -> int:
        factor = math.log(256) / math.log(self._alpha_len)
        return int(math.ceil(factor * num_bytes))


_global_instance = ShortUUID()
encode = _global_instance.encode
decode = _global_instance.decode
uuid = _global_instance.uuid
random = _global_instance.random
get_alphabet = _global_instance.get_alphabet
set_alphabet = _global_instance.set_alphabet
