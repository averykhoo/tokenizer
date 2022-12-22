import random
import re

import unicodedata

from regex_tokenizer import _REGEX_GRAPHEME
from regex_tokenizer import _REGEX_WORD_CHAR
from upside_down import flip_text

RE_ZALGO = re.compile(r'(?:.[\u0300-\u036F\u0488\u0489]+)+(?:(?:\s+|[^\w])(?:.[\u0300-\u036F\u0488\u0489]+)+)*')


def sad_face(text: str):
    # return text.replace('', '\u0311\u0308')[2:]  # substitute whitespace
    return re.sub(r'([^\s])', '\\1\u0311\u0308', text)  # don't modify whitespace


def add_random_faces(text: str) -> str:
    mouths = [
        '◌̆',  # breve
        '◌̌',  # caron
        '◌̑',  # inverted breve
        '◌̂',  # circumflex
        '◌̄',  # macron
        '◌̃',  # tilde
        '◌̅',  # double macron
        '◌͆',  # bridge
        '◌̽',  # x
        '◌̊',  # ring
    ]

    # skip those two since they're not reversible
    eyes = [
        '◌̈',  # diaresis
        # '◌̋',  # double acute
        '◌̎',  # double vertical line
        # '◌̏',  # double grave
    ]

    out = []
    for char in _REGEX_GRAPHEME.findall(text):
        out.append(char)
        if _REGEX_WORD_CHAR.match(char) is not None:
            out.append(random.choice(mouths)[1])
            out.append(random.choice(eyes)[1])
    return ''.join(out)


def simple_zalgo(text: str, n_chars: int = 10):
    out = []

    for char in text:
        out.append(char)

        if char.isspace():
            continue

        for _ in range(n_chars):
            out.append(chr(random.randint(0x300, 0x36f)))

    return ''.join(out)


def unzalgo(text: str):
    out = []
    for char in text:
        if 0x300 <= ord(char) <= 0x36F or ord(char) in {0x488, 0x489}:
            continue
        out.append(char)

    return ''.join(out)


def is_zalgo(text: str):
    n_zalgo = 0
    n_normal = 0
    for char in text:
        if 0x300 <= ord(char) <= 0x36F or ord(char) in {0x488, 0x489}:
            n_zalgo += 1
        elif not char.isspace():
            n_normal += 1
    return n_zalgo > n_normal


ZALGO_CHAR_ABOVE = ['\u030D', '\u030E', '\u0304', '\u0305', '\u033F',
                    '\u0311', '\u0306', '\u0310', '\u0352', '\u0357',
                    '\u0351', '\u0307', '\u0308', '\u030A', '\u0342',
                    '\u0343', '\u0344', '\u034A', '\u034B', '\u034C',
                    '\u0303', '\u0302', '\u030C', '\u0350', '\u0300',
                    '\u0301', '\u030B', '\u030F', '\u0312', '\u0313',
                    '\u0314', '\u033D', '\u0309', '\u0363', '\u0364',
                    '\u0365', '\u0366', '\u0367', '\u0368', '\u0369',
                    '\u036A', '\u036B', '\u036C', '\u036D', '\u036E',
                    '\u036F', '\u033E', '\u035B', '\u0346', '\u031A']  # above the text

ZALGO_CHAR_MIDDLE = ['\u0315', '\u031B', '\u0340', '\u0341', '\u0358',
                     '\u0321', '\u0322', '\u0327', '\u0328', '\u0334',
                     '\u0335', '\u0336', '\u034F', '\u035C', '\u035D',
                     '\u035E', '\u035F', '\u0360', '\u0362', '\u0338',
                     '\u0337', '\u0361', '\u0488', '\u0489']  # on the same line as the text

ZALGO_CHAR_BELOW = ['\u0316', '\u0317', '\u0318', '\u0319', '\u031C',
                    '\u031D', '\u031E', '\u031F', '\u0320', '\u0324',
                    '\u0325', '\u0326', '\u0329', '\u032A', '\u032B',
                    '\u032C', '\u032D', '\u032E', '\u032F', '\u0330',
                    '\u0331', '\u0332', '\u0333', '\u0339', '\u033A',
                    '\u033B', '\u033C', '\u0345', '\u0347', '\u0348',
                    '\u0349', '\u034D', '\u034E', '\u0353', '\u0354',
                    '\u0355', '\u0356', '\u0359', '\u035A', '\u0323']  # below the text


# https://gist.github.com/MetroWind/1401473/4631da7a4540a63e72701792a4aa0262acc7d397
def zalgo(text: str,
          n_above: int = 2,
          n_middle: int = 1,
          n_below: int = 5,
          allow_repeat: bool = True,
          ) -> str:
    out = []
    for char in text:
        out.append(char)
        if char.isspace():
            continue

        z_chars = []
        if allow_repeat:
            z_chars.extend(random.choices(ZALGO_CHAR_ABOVE, k=n_above))
            z_chars.extend(random.choices(ZALGO_CHAR_MIDDLE, k=n_middle))
            z_chars.extend(random.choices(ZALGO_CHAR_BELOW, k=n_below))
        else:
            z_chars.extend(random.sample(ZALGO_CHAR_ABOVE, n_above))
            z_chars.extend(random.sample(ZALGO_CHAR_MIDDLE, n_middle))
            z_chars.extend(random.sample(ZALGO_CHAR_BELOW, n_above))
        random.shuffle(z_chars)
        out.extend(z_chars)

    return ''.join(out)


# https://stackoverflow.com/questions/22277052/how-can-z͎̠͗ͣḁ̵͙̑l͖͙̫̲̉̃ͦ̾͊ͬ̀g͔̤̞͓̐̓̒̽o͓̳͇̔ͥ-text-be-prevented
def aggressive_is_zalgo(text: str):
    n_zalgo = 0
    n_normal = 0
    for char in unicodedata.normalize('NFD', text):
        if unicodedata.category(char) in {'Mn', 'Me'}:
            n_zalgo += 1
        elif not char.isspace():
            n_normal += 1
    return n_zalgo > n_normal


# https://stackoverflow.com/questions/22277052/how-can-z͎̠͗ͣḁ̵͙̑l͖͙̫̲̉̃ͦ̾͊ͬ̀g͔̤̞͓̐̓̒̽o͓̳͇̔ͥ-text-be-prevented
def aggressive_unzalgo(text):
    out = []
    for char in unicodedata.normalize('NFD', text):
        if unicodedata.category(char) in {'Mn', 'Me'}:
            continue
        out.append(char)

    return ''.join(out)


if __name__ == '__main__':
    text = 'hello world'
    print(text)

    z1 = simple_zalgo(text)
    print(z1)

    z2 = zalgo(text)
    print(z2)

    print(unzalgo(z1))
    print(unzalgo(z2))
    print(aggressive_unzalgo(z1))
    print(aggressive_unzalgo(z2))

    print(add_random_faces(text))
    print(aggressive_unzalgo(add_random_faces(text)))
    print(add_random_faces(text))
    print(add_random_faces(text))
    print(add_random_faces(text))
    print(flip_text(add_random_faces(text)))
    print(flip_text(add_random_faces(text)))

    print(flip_text(add_random_faces('''[rapid] 2022-12-20 12:00:00
Keycloak: 12/12 checks are up
RAPID: 12/12 checks are up
Scoold: 1/1 checks are up''')))
