# coding: utf-8
"""
    captcha.audio
    ~~~~~~~~~~~~~

    Generate Audio CAPTCHAs, with built-in digits CAPTCHA.

    This module is totally inspired by https://github.com/dchest/captcha
"""

import typing as t
import os
import copy
import wave
import struct
import random
import operator
from functools import reduce


__all__ = ['AudioCaptcha']

WAVE_SAMPLE_RATE = 8000  # HZ
WAVE_HEADER = bytearray(
    b'RIFF\x00\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00'
    b'@\x1f\x00\x00@\x1f\x00\x00\x01\x00\x08\x00data'
)
WAVE_HEADER_LENGTH = len(WAVE_HEADER) - 4
DATA_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data')


def _read_wave_file(filepath: str) -> bytearray:
    w = wave.open(filepath)
    data = w.readframes(-1)
    w.close()
    return bytearray(data)


def change_speed(body: bytearray, speed: float = 1) -> bytearray:
    """Change the voice speed of the wave body."""
    if speed == 1:
        return body

    length = int(len(body) * speed)
    rv = bytearray(length)

    step: float = 0
    for v in body:
        i = int(step)
        while i < int(step + speed) and i < length:
            rv[i] = v
            i += 1
        step += speed
    return rv


def patch_wave_header(body: bytearray) -> bytearray:
    """Patch header to the given wave body.

    :param body: the wave content body, it should be bytearray.
    """
    length = len(body)

    padded = length + length % 2
    total = WAVE_HEADER_LENGTH + padded

    header = copy.copy(WAVE_HEADER)
    # fill the total length position
    header[4:8] = bytearray(struct.pack('<I', total))
    header += bytearray(struct.pack('<I', length))

    data = header + body

    # the total length is even
    if length != padded:
        data = data + bytearray([0])

    return data


def create_noise(length: int, level: int = 4) -> bytearray:
    """Create white noise for background"""
    noise = bytearray(length)
    adjust = 128 - int(level / 2)
    i = 0
    while i < length:
        v = random.randint(0, 256)
        noise[i] = v % level + adjust
        i += 1
    return noise


def create_silence(length: int) -> bytearray:
    """Create a piece of silence."""
    data = bytearray(length)
    i = 0
    while i < length:
        data[i] = 128
        i += 1
    return data


def change_sound(body: bytearray, level: float = 1) -> bytearray:
    if level == 1:
        return body

    body = copy.copy(body)
    for i, v in enumerate(body):
        if v > 128:
            v = int((v - 128) * level + 128)
            v = max(v, 128)
            v = min(v, 255)
        elif v < 128:
            v = int(128 - (128 - v) * level)
            v = min(v, 128)
            v = max(v, 0)
        body[i] = v
    return body


def mix_wave(src: bytearray, dst: bytearray) -> bytearray:
    """Mix two wave body into one."""
    if len(src) > len(dst):
        # output should be longer
        dst, src = src, dst

    for i, sv in enumerate(src):
        dv = dst[i]
        if sv < 128 and dv < 128:
            dst[i] = int(sv * dv / 128)
        else:
            dst[i] = int(2 * (sv + dv) - sv * dv / 128 - 256)
    return dst


BEEP = _read_wave_file(os.path.join(DATA_DIR, 'beep.wav'))
END_BEEP = change_speed(BEEP, 1.4)
SILENCE = create_silence(int(WAVE_SAMPLE_RATE / 5))


class AudioCaptcha:
    """Create an audio CAPTCHA.

    Create an instance of AudioCaptcha is pretty simple::

        captcha = AudioCaptcha()
        captcha.write('1234', 'out.wav')

    This module has a built-in digits CAPTCHA, but it is suggested that you
    create your own voice data library. A voice data library is a directory
    that contains lots of single charater named directories, for example::

        voices/
            0/
            1/
            2/

    The single charater named directories contain the wave files which pronunce
    the directory name. A charater directory can has many wave files, this
    AudioCaptcha will randomly choose one of them.

    You should always use your own voice library::

        captcha = AudioCaptcha(voicedir='/path/to/voices')
    """
    def __init__(self, voicedir: t.Optional[str] = None):
        if voicedir is None:
            voicedir = DATA_DIR

        self._voicedir = voicedir
        self._cache: t.Dict[str, t.List[bytearray]] = {}
        self._choices: t.List[str] = []

    @property
    def choices(self) -> t.List[str]:
        """Available choices for characters to be generated."""
        if self._choices:
            return self._choices
        for n in os.listdir(self._voicedir):
            if len(n) == 1 and os.path.isdir(os.path.join(self._voicedir, n)):
                self._choices.append(n)
        return self._choices

    def random(self, length: int = 6) -> t.List[str]:
        """Generate a random string with the given length.

        :param length: the return string length.
        """
        return random.sample(self.choices, length)

    def load(self) -> None:
        """Load voice data into memory."""
        for name in self.choices:
            self._load_data(name)

    def _load_data(self, name: str) -> None:
        dirname = os.path.join(self._voicedir, name)
        data: t.List[bytearray] = []
        for f in os.listdir(dirname):
            filepath = os.path.join(dirname, f)
            if f.endswith('.wav') and os.path.isfile(filepath):
                data.append(_read_wave_file(filepath))
        self._cache[name] = data

    def _twist_pick(self, key: str) -> bytearray:
        voice = random.choice(self._cache[key])

        # random change speed
        speed = random.randrange(90, 120) / 100.0
        voice = change_speed(voice, speed)

        # random change sound
        level = random.randrange(80, 120) / 100.0
        voice = change_sound(voice, level)
        return voice

    def _noise_pick(self) -> bytearray:
        key = random.choice(self.choices)
        voice = random.choice(self._cache[key])
        voice = copy.copy(voice)
        voice.reverse()

        speed = random.randrange(8, 16) / 10.0
        voice = change_speed(voice, speed)

        level = random.randrange(2, 6) / 10.0
        voice = change_sound(voice, level)
        return voice

    def create_background_noise(self, length: int, chars: str) -> bytearray:
        noise = create_noise(length, 4)
        pos = 0
        while pos < length:
            sound = self._noise_pick()
            end = pos + len(sound) + 1
            noise[pos:end] = mix_wave(sound, noise[pos:end])
            pos = end + random.randint(0, int(WAVE_SAMPLE_RATE / 10))
        return noise

    def create_wave_body(self, chars: str) -> bytearray:
        voices: t.List[bytearray] = []
        inters: t.List[int] = []
        for c in chars:
            voices.append(self._twist_pick(c))
            i = random.randint(WAVE_SAMPLE_RATE, WAVE_SAMPLE_RATE * 3)
            inters.append(i)

        durations = map(lambda a: len(a), voices)
        length = max(durations) * len(chars) + reduce(operator.add, inters)
        bg = self.create_background_noise(length, chars)

        # begin
        pos: int = inters[0]
        for i, v in enumerate(voices):
            end = pos + len(v) + 1
            bg[pos:end] = mix_wave(v, bg[pos:end])
            pos = end + inters[i]

        return BEEP + SILENCE + BEEP + SILENCE + BEEP + bg + END_BEEP

    def generate(self, chars: str) -> bytearray:
        """Generate audio CAPTCHA data. The return data is a bytearray.

        :param chars: text to be generated.
        """
        if not self._cache:
            self.load()
        body = self.create_wave_body(chars)
        return patch_wave_header(body)

    def write(self, chars: str, output: str) -> None:
        """Generate and write audio CAPTCHA data to the output.

        :param chars: text to be generated.
        :param output: output destionation.
        """
        data = self.generate(chars)
        with open(output, 'wb') as f:
            f.write(data)
