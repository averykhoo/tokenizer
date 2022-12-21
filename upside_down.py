import re
import string
import unicodedata

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
    '"':  '„﮼',
    '#':  '#',
    '$':  '$',
    '%':  '%',
    '&':  '⅋',
    "'":  '⸲,╻',
    '(':  ')',
    ')':  '(',
    '*':  '⁎*',
    '+':  '+',
    ',':  "‘ʻ'`",
    '-':  '-',
    '.':  '˙',
    '/':  '/',
    '0':  '0',
    '1':  '⥝ƖІ⇂',
    '2':  '↊ᄅᘔⵒ',
    '3':  '↋ƐԐԑ',
    '4':  'ᔭㄣߤ',
    '5':  'ϛϚ',
    '6':  '9ƍ',
    '7':  '𝘓Ɫ∠ㄥ',
    '8':  '8',
    '9':  '6δẟ',
    ':':  ':',
    ';':  '⸵؛',
    '<':  '>',
    '=':  '=',
    '>':  '<',
    '?':  '¿',
    '@':  '@',
    'A':  'Ɐ∀ᗄ',
    'B':  'ꓭᗺξ𐐒ჵ',
    'C':  'ƆϽↃ',
    'D':  'ᗡ◖',
    'E':  'Ǝ⁆ᴲ∃ⱻ',
    'F':  'Ⅎ߃ᖵⅎ',
    'G':  '⅁פ',
    'H':  'H',
    'I':  'I',
    'J':  'ᒋſ',
    'K':  'Ʞ⋊ꓘ',
    'L':  'Ꞁ˥ᒣ⅂',
    'M':  'ꟽWƜ',
    'N':  'NИᴎ',  # 2 of these are mirrored, not upside down...
    'O':  'O',
    'P':  'Ԁ',
    'Q':  'ΌὉꝹ',
    'R':  'ꓤᴚʁ',  # the last one is mirrored, but you never know what you'll find out there
    'S':  'SՏ',
    'T':  'Ʇ⊥┴ꓕ',
    'U':  '∩ႶՈ',
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
    'a':  'ɐɒᵄ',
    'b':  'qꟼ',
    'c':  'ↄɔͻ',
    'd':  'p',
    'e':  'ǝ',
    'f':  'ɟֈ',
    'g':  'ᵷƃ',
    'h':  'ɥʮʯꞍկ',
    'i':  'ᴉıⵑ℩',
    'j':  'ṛɾ',
    'k':  'ʞ',
    'l':  'ꞁlʃʅן',
    'm':  'ɯꟺwա',
    'n':  'uս',
    'o':  'o',
    'p':  'd',
    'q':  'b',
    'r':  'ɹɺʴ',
    's':  's',
    't':  'ʇ⸸',
    'u':  'nո',
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
NON_ASCII = {
    '⁅':  '⁆',
    '∴':  '∵',
    '⁀':  '‿',
    '―':  '―',
    '\0': '\0',
    '\2': '\3',
    '\b': '\b',
    '‽':  '⸘',
    '⛤':  '⛧',
    'ʔ':  'ʖ',
    'œ':  'ᴔ',
    'æ':  'ᴂᵆæ',
    '⬟':  '⯂',
    '†':  '⸸',
}

_INVERTED_PRINTABLE = dict()
for _char, _upside_down in PRINTABLE.items():
    for _upside_down_char in _upside_down:
        _INVERTED_PRINTABLE.setdefault(_upside_down_char, _char)

_INVERTED_NON_ASCII = dict()
for _char, _upside_down in NON_ASCII.items():
    for _upside_down_char in _upside_down:
        _INVERTED_NON_ASCII.setdefault(_upside_down_char, _char)

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
    for _from, _to in TRANSLITERATIONS.items():
        text = text.replace(_from, _to)

    char_maps = [PRINTABLE, _INVERTED_PRINTABLE, NON_ASCII, _INVERTED_NON_ASCII]
    if is_flipped_ascii(text):
        char_maps.reverse()

    out = []
    flipped_grapheme = []
    for grapheme in _REGEX_GRAPHEME.findall(text):
        grapheme = unicodedata.normalize('NFKD', grapheme)
        for char_map in char_maps:
            if grapheme[0] in char_map:
                flipped_grapheme.append(char_map[grapheme[0]][0])
                break
        else:
            flipped_grapheme.append('\uFFFD')

        for diacritic in grapheme[1:]:
            if diacritic in DIACRITICS:
                flipped_grapheme.append(DIACRITICS[diacritic])
            elif diacritic in _INVERTED_DIACRITICS:
                flipped_grapheme.append(_INVERTED_DIACRITICS[diacritic])

        out.append(''.join(flipped_grapheme))
        flipped_grapheme.clear()

    out.reverse()
    return ''.join(out)


def unflip_upside_down_words(text: str) -> str:
    out = []
    unflipped = []
    maybe_unflipped = []
    for token in word_tokenize(text, include_non_word_chars=True):
        if is_flipped_ascii(token):
            unflipped.extend(maybe_unflipped)
            maybe_unflipped.clear()
            unflipped.append(flip_text(token))
        elif _REGEX_WORD_CHAR.match(token) is None:
            if unflipped:
                if flip_text(token) == token:
                    maybe_unflipped.append(token)
                else:
                    unflipped.extend(maybe_unflipped)
                    maybe_unflipped.clear()
                    unflipped.append(flip_text(token))
            else:
                out.append(token)
        else:
            unflipped.reverse()
            out.extend(unflipped)
            unflipped.clear()
            maybe_unflipped.reverse()
            out.extend(maybe_unflipped)
            maybe_unflipped.clear()
            out.append(token)

    return ''.join(out + unflipped[::-1] + maybe_unflipped[::-1])


if __name__ == '__main__':
    for char, upside_down in PRINTABLE.items():
        print('-' * 100)
        print(repr(char))
        for upside_down_char in upside_down:
            try:
                print('  ', repr(upside_down_char), unicodedata.name(upside_down_char))
            except ValueError:
                print('  ', repr(upside_down_char), f'U+{ord(upside_down_char):04x}')

    for char in string.printable:
        if flip_text(flip_text(char)) != char:
            print(repr(char), repr(flip_text(char)), repr(flip_text(flip_text(char))))
    print('0', repr(string.printable))
    print('1', repr(flip_text(string.printable)))
    print('2', repr(flip_text(flip_text(string.printable))))
    print('3', repr(flip_text(flip_text(flip_text(string.printable)))))
    print(flip_text('hello_world HELLO WORLD test '))
    print(flip_text(string.printable.split()[0]))
    print(flip_text(
        '''~{|}`‾^[\\]@¿<=>;:/.-ʻ+*()╻\⅋%$#﮼¡Z⅄XϺɅՈꓕSꓤꝹԀONꟽ⅂ꓘᒋIH⅁ᖵƎᗡϽꓭ∀zʎxʍʌnʇsɹbdouɯʅʞɾᴉɥƃⅎǝpɔqɐ68𝘓95ߤ↋↊⇂0'''))

    print(unflip_upside_down_words('normal_pꞁɹoʍ‾oꞁꞁǝɥ_text  NORMAL ᗡꞀᴚOϺ OꞀꞀƎH TEXT  normal pꞁɹoʍ oꞁꞁǝɥ text  ʇsǝʇ '))

    print(flip_text('köln'))
