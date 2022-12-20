import re
import string

from regex_tokenizer import _REGEX_GRAPHEME
from regex_tokenizer import _REGEX_WORD_CHAR
from regex_tokenizer import word_tokenize

DIACRITICS = {
    '̈': '̤',
    '̊': '̥',
    '́': '̗',
    '̀': '̖',
    '̇': '̣',
    '̃': '̰',
    '̄': '̱',
    '̂': '̬',
    '̆': '̯',
    '̌': '̭',
    '̑': '̮',
    '̍': '̩',
}

TRANSLITERATIONS = {'ß': 'ss'}

PRINTABLE = {
    '!':  '¡',
    '"':  '„',
    '#':  '#',
    '$':  '$',
    '%':  '%',
    '&':  '⅋',
    "'":  '⸲,',
    '(':  ')',
    ')':  '(',
    '*':  '*⁎',
    '+':  '+',
    ',':  "‘ʻ'`",
    '-':  '-',
    '.':  '˙',
    '/':  '/',
    '0':  '0',
    '1':  'ƖІ⇂⥝',
    '2':  '↊ᄅᘔⵒ',
    '3':  '↋ƐԐԑ',
    '4':  'ᔭㄣ',
    '5':  'Ϛϛ',
    '6':  '9',
    '7':  '∠Ɫㄥ',
    '8':  '8',
    '9':  '6',
    ':':  ':',
    ';':  '؛⸵',
    '<':  '>',
    '=':  '=',
    '>':  '<',
    '?':  '¿',
    '@':  '@',
    'A':  'Ɐ∀ᗄ',
    'B':  'ᗺξ𐐒ჵ',
    'C':  'ƆϽↃ',
    'D':  'ᗡ◖',
    'E':  'Ǝ⁆ᴲ∃ⱻ',
    'F':  '߃ℲᖵℲ',
    'G':  'פ⅁',
    'H':  'H',
    'I':  'I',
    'J':  'ſᒋ',
    'K':  'Ʞ⋊',
    'L':  'Ꞁ˥ᒣ⅂⅂',
    'M':  'ꟽWƜ',
    'N':  'NИᴎ',  # 2 of these are reversed, not upside down...
    'O':  'O',
    'P':  'Ԁ',
    'Q':  'QΌὉꝹ',
    'R':  'ᴚʁ',
    'S':  'S',
    'T':  'Ʇ⊥┴',
    'U':  'Ⴖ∩',
    'V':  'ɅΛᴧ',
    'W':  'ϺΜM',
    'X':  'X',
    'Y':  '⅄',
    'Z':  'Z',
    '[':  ']',
    '\\': '\\',
    ']':  '[',
    '^':  'ᵥ',
    '_':  '‾',
    '`':  ',',
    'a':  'ɐɒ',
    'b':  'q',
    'c':  'ↄɔͻ',
    'd':  'p',
    'e':  'ǝ',
    'f':  'ɟ',
    'g':  'ᵷƃ',
    'h':  'ɥʮʯꞍ',
    'i':  'ᴉıⵑ',
    'j':  'ṛɾ',
    'k':  'ʞ',
    'l':  'ꞁlʃʅן',
    'm':  'ɯꟺw',
    'n':  'u',
    'o':  'o',
    'p':  'd',
    'q':  'b',
    'r':  'ɹ',
    's':  's',
    't':  'ʇ',
    'u':  'n',
    'v':  'ʌ',
    'w':  'ʍm',
    'x':  'x',
    'y':  'ʎλ',
    'z':  'z',
    '{':  '}',
    '|':  '|',
    '}':  '{',
    '~':  '~',
    ' ':  ' ',
    '\t': '\t',
    '\n': '\n',
    '\r': '\r',
    '\v': '\v',
    '\f': '\f',
}
UNPRINTABLE = {
    '⁅':  '⁆',
    '∴':  '∵',
    '⁀':  '‿',
    '―':  '―',
    '\0': '\0',
    '\2': '\3',
    '\b': '\b',
}

_INVERTED_PRINTABLE = dict()
for _char, _upside_down in PRINTABLE.items():
    for _upside_down_char in _upside_down:
        _INVERTED_PRINTABLE.setdefault(_upside_down_char, _char)

_INVERTED_UNPRINTABLE = dict()
for _char, _upside_down in UNPRINTABLE.items():
    for _upside_down_char in _upside_down:
        _INVERTED_UNPRINTABLE.setdefault(_upside_down_char, _char)

_INVERTED_DIACRITICS = dict()
for _char, _upside_down in DIACRITICS.items():
    for _upside_down_char in _upside_down:
        _INVERTED_DIACRITICS.setdefault(_upside_down_char, _char)

_FLIPPED_CHARS = set()
for _char, _upside_down in PRINTABLE.items():
    _FLIPPED_CHARS.update(_upside_down)
REGEX_FLIPPED_CHAR = re.compile(f'^[{re.escape("".join(_FLIPPED_CHARS))}]+$')
REGEX_PRINTABLE = re.compile(f'^[{re.escape(string.printable)}]$')


def is_flipped_ascii(text: str) -> bool:
    if REGEX_PRINTABLE.fullmatch(text):
        return False
    return REGEX_FLIPPED_CHAR.fullmatch(text) is not None


def flip_text(text: str) -> str:
    char_maps = [PRINTABLE, _INVERTED_PRINTABLE, UNPRINTABLE, _INVERTED_UNPRINTABLE]
    if is_flipped_ascii(text):
        char_maps.reverse()

    out = []
    for grapheme in _REGEX_GRAPHEME.findall(text):
        for char_map in char_maps:
            if grapheme[0] in char_map:
                out.append(char_map[grapheme[0]][0])
                break
        else:
            out.append('\uFFFD')

        for diacritic in grapheme[1:]:
            if diacritic in DIACRITICS:
                out.append(DIACRITICS[diacritic])
            elif diacritic in _INVERTED_DIACRITICS:
                out.append(_INVERTED_DIACRITICS[diacritic])

    out.reverse()
    return ''.join(out)


def unflip_upside_down_words(text: str) -> str:
    # todo: fix weird edge cases with whitespace before and after flipped text
    out = []
    unflipped = []
    for word in word_tokenize(text, include_non_word_chars=True):
        if is_flipped_ascii(word):
            unflipped.append(flip_text(word))
        elif unflipped and _REGEX_WORD_CHAR.match(word) is None:
            unflipped.append(flip_text(word))
        else:
            out.append(word)
            unflipped.reverse()
            out.extend(unflipped)
            unflipped.clear()

    return ''.join(out + unflipped[::-1])


if __name__ == '__main__':
    for char in string.printable:
        if flip_text(flip_text(char)) != char:
            print(repr(char), repr(flip_text(char)), repr(flip_text(flip_text(char))))
    print(flip_text(flip_text(string.printable)))

    print(flip_text('hello_world HELLO WORLD'))

    print(unflip_upside_down_words('normal_text pꞁɹoʍ‾oꞁꞁǝɥ NORMAL TEXT ᗡꞀᴚOϺ OꞀꞀƎH normal text pꞁɹoʍ oꞁꞁǝɥ'))
