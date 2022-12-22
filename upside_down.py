import string
import warnings

import regex
import unicodedata

from regex_tokenizer import word_tokenize  # only needed to intelligently detect and un-flip words in a string

REGEX_GRAPHEME = regex.compile(r'\X', flags=regex.UNICODE)  # builtins.re does not support `\X`
REGEX_WORD_CHAR = regex.compile(r'\w', flags=regex.UNICODE)

# inspired by https://github.com/cburgmer/upsidedown
DIACRITICS = {
    "◌̀": "◌̖",  # COMBINING GRAVE ACCENT -> COMBINING GRAVE ACCENT BELOW
    "◌́": "◌̗",  # COMBINING ACUTE ACCENT -> COMBINING ACUTE ACCENT BELOW
    "◌̂": "◌̬",  # COMBINING CIRCUMFLEX ACCENT -> COMBINING CARON BELOW
    "◌̃": "◌̰",  # COMBINING TILDE -> COMBINING TILDE BELOW
    "◌̄": "◌̱",  # COMBINING MACRON -> COMBINING MACRON BELOW
    "◌̅": "◌̲",  # COMBINING OVERLINE -> COMBINING LOW LINE
    "◌̆": "◌̯",  # COMBINING BREVE -> COMBINING INVERTED BREVE BELOW
    "◌̇": "◌̣",  # COMBINING DOT ABOVE -> COMBINING DOT BELOW
    "◌̈": "◌̤",  # COMBINING DIAERESIS -> COMBINING DIAERESIS BELOW
    "◌̊": "◌̥",  # COMBINING RING ABOVE -> COMBINING RING BELOW
    "◌̌": "◌̭",  # COMBINING CARON -> COMBINING CIRCUMFLEX ACCENT BELOW
    "◌̍": "◌̩",  # COMBINING VERTICAL LINE ABOVE -> COMBINING VERTICAL LINE BELOW
    "◌̎": "◌͈",  # COMBINING DOUBLE VERTICAL LINE ABOVE -> COMBINING DOUBLE VERTICAL LINE BELOW
    "◌̑": "◌̮",  # COMBINING INVERTED BREVE -> COMBINING BREVE BELOW
    "◌̓": "◌̦",  # COMBINING COMMA ABOVE -> COMBINING COMMA BELOW
    "◌̴": "◌̴",  # COMBINING TILDE OVERLAY -> COMBINING TILDE OVERLAY
    "◌̵": "◌̵",  # COMBINING SHORT STROKE OVERLAY -> COMBINING SHORT STROKE OVERLAY
    "◌̶": "◌̶",  # COMBINING LONG STROKE OVERLAY -> COMBINING LONG STROKE OVERLAY
    "◌̷": "◌̷",  # COMBINING SHORT SOLIDUS OVERLAY -> COMBINING SHORT SOLIDUS OVERLAY
    "◌̸": "◌̸",  # COMBINING LONG SOLIDUS OVERLAY -> COMBINING LONG SOLIDUS OVERLAY
    "◌̽": "◌͓",  # COMBINING X ABOVE -> COMBINING X BELOW
    "◌̿": "◌̳",  # COMBINING DOUBLE OVERLINE -> COMBINING DOUBLE LOW LINE
    "◌͆": "◌̺",  # COMBINING BRIDGE ABOVE -> COMBINING INVERTED BRIDGE BELOW
    "◌͌": "◌᷽",  # COMBINING ALMOST EQUAL TO ABOVE -> COMBINING ALMOST EQUAL TO BELOW
    "◌͐": "◌͔",  # COMBINING RIGHT ARROWHEAD ABOVE -> COMBINING LEFT ARROWHEAD BELOW
    "◌͑": "◌̹",  # COMBINING LEFT HALF RING ABOVE -> COMBINING RIGHT HALF RING BELOW
    "◌͗": "◌̜",  # COMBINING RIGHT HALF RING ABOVE -> COMBINING LEFT HALF RING BELOW
    "◌͛": "◌᷏",  # COMBINING ZIGZAG ABOVE -> COMBINING ZIGZAG BELOW
    "◌͝": "◌᷼",  # COMBINING DOUBLE BREVE -> COMBINING DOUBLE INVERTED BREVE BELOW
    "◌͞": "◌͟",  # COMBINING DOUBLE MACRON -> COMBINING DOUBLE MACRON BELOW
    "◌͡": "◌͜",  # COMBINING DOUBLE INVERTED BREVE -> COMBINING DOUBLE BREVE BELOW
    # "◌ͬ": "◌᷊",  # COMBINING LATIN SMALL LETTER R -> COMBINING LATIN SMALL LETTER R BELOW
    "◌ٔ": "◌ٕ",  # ARABIC HAMZA ABOVE -> ARABIC HAMZA BELOW
    "◌ܰ": "◌ܱ",  # SYRIAC PTHAHA ABOVE -> SYRIAC PTHAHA BELOW
    "◌ܳ": "◌ܴ",  # SYRIAC ZQAPHA ABOVE -> SYRIAC ZQAPHA BELOW
    "◌ܶ": "◌ܷ",  # SYRIAC RBASA ABOVE -> SYRIAC RBASA BELOW
    "◌ܺ": "◌ܻ",  # SYRIAC HBASA ABOVE -> SYRIAC HBASA BELOW
    "◌ܽ": "◌ܾ",  # SYRIAC ESASA ABOVE -> SYRIAC ESASA BELOW
    "◌݃": "◌݄",  # SYRIAC TWO VERTICAL DOTS ABOVE -> SYRIAC TWO VERTICAL DOTS BELOW
    "◌݅": "◌݆",  # SYRIAC THREE DOTS ABOVE -> SYRIAC THREE DOTS BELOW
    "◌݇": "◌݈",  # SYRIAC OBLIQUE LINE ABOVE -> SYRIAC OBLIQUE LINE BELOW
    "◌࣪": "◌࣭",  # ARABIC TONE ONE DOT ABOVE -> ARABIC TONE ONE DOT BELOW
    "◌࣫": "◌࣮",  # ARABIC TONE TWO DOTS ABOVE -> ARABIC TONE TWO DOTS BELOW
    "◌࣬": "◌࣯",  # ARABIC TONE LOOP ABOVE -> ARABIC TONE LOOP BELOW
    "◌ࣷ": "◌ࣺ",  # ARABIC LEFT ARROWHEAD ABOVE -> ARABIC RIGHT ARROWHEAD BELOW
    "◌ࣸ": "◌ࣹ",  # ARABIC RIGHT ARROWHEAD ABOVE -> ARABIC LEFT ARROWHEAD BELOW
    "◌ᩳ": "◌ᩬ",  # TAI THAM VOWEL SIGN OA ABOVE -> TAI THAM VOWEL SIGN OA BELOW
    "◌᪻": "◌᪽",  # COMBINING PARENTHESES ABOVE -> COMBINING PARENTHESES BELOW
    "◌᳴": "◌᳘",  # VEDIC TONE CANDRA ABOVE -> VEDIC TONE CANDRA BELOW
    # "◌ᷱ": "◌ᪿ",  # COMBINING LATIN SMALL LETTER W -> COMBINING LATIN SMALL LETTER W BELOW
    "◌᷵": "◌̞",  # COMBINING UP TACK ABOVE -> COMBINING DOWN TACK BELOW
    "◌᷾": "◌͕",  # COMBINING LEFT ARROWHEAD ABOVE -> COMBINING RIGHT ARROWHEAD BELOW
    "◌⃒": "◌⃒",  # COMBINING LONG VERTICAL LINE OVERLAY -> COMBINING LONG VERTICAL LINE OVERLAY
    "◌⃓": "◌⃓",  # COMBINING SHORT VERTICAL LINE OVERLAY -> COMBINING SHORT VERTICAL LINE OVERLAY
    "◌⃖": "◌⃯",  # COMBINING LEFT ARROW ABOVE -> COMBINING RIGHT ARROW BELOW
    "◌⃗": "◌⃮",  # COMBINING RIGHT ARROW ABOVE -> COMBINING LEFT ARROW BELOW
    # "◌⃘": "◌⃘",  # COMBINING RING OVERLAY -> COMBINING RING OVERLAY
    # "◌⃙": "◌⃙",  # COMBINING CLOCKWISE RING OVERLAY -> COMBINING CLOCKWISE RING OVERLAY
    # "◌⃚": "◌⃚",  # COMBINING ANTICLOCKWISE RING OVERLAY -> COMBINING ANTICLOCKWISE RING OVERLAY
    "◌⃥": "◌⃥",  # COMBINING REVERSE SOLIDUS OVERLAY -> COMBINING REVERSE SOLIDUS OVERLAY
    "◌⃦": "◌⃦",  # COMBINING DOUBLE VERTICAL STROKE OVERLAY -> COMBINING DOUBLE VERTICAL STROKE OVERLAY
    "◌⃩": "◌᷹",  # COMBINING WIDE BRIDGE ABOVE -> COMBINING WIDE INVERTED BRIDGE BELOW
    # "◌⃪": "◌⃪",  # COMBINING LEFTWARDS ARROW OVERLAY -> COMBINING LEFTWARDS ARROW OVERLAY
    "◌⃫": "◌⃫",  # COMBINING LONG DOUBLE SOLIDUS OVERLAY -> COMBINING LONG DOUBLE SOLIDUS OVERLAY
    "◌⃰": "◌͙",  # COMBINING ASTERISK ABOVE -> COMBINING ASTERISK BELOW
    "◌︠": "◌︨",  # COMBINING LIGATURE LEFT HALF -> COMBINING LIGATURE RIGHT HALF BELOW
    "◌︡": "◌︧",  # COMBINING LIGATURE RIGHT HALF -> COMBINING LIGATURE LEFT HALF BELOW
    "◌︤": "◌︬",  # COMBINING MACRON LEFT HALF -> COMBINING MACRON RIGHT HALF BELOW
    "◌︥": "◌︫",  # COMBINING MACRON RIGHT HALF -> COMBINING MACRON LEFT HALF BELOW
    "◌︦": "◌︭",  # COMBINING CONJOINING MACRON -> COMBINING CONJOINING MACRON BELOW
    "◌𐫥": "◌𐫦",  # MANICHAEAN ABBREVIATION MARK ABOVE -> MANICHAEAN ABBREVIATION MARK BELOW
    "◌𐽈": "◌𐽆",  # SOGDIAN COMBINING DOT ABOVE -> SOGDIAN COMBINING DOT BELOW
    "◌𐽉": "◌𐽇",  # SOGDIAN COMBINING TWO DOTS ABOVE -> SOGDIAN COMBINING TWO DOTS BELOW
    "◌𐽊": "◌𐽋",  # SOGDIAN COMBINING CURVE ABOVE -> SOGDIAN COMBINING CURVE BELOW
    "◌𐽌": "◌𐽍",  # SOGDIAN COMBINING HOOK ABOVE -> SOGDIAN COMBINING HOOK BELOW
    # "◌𖾑": "◌𖾒",  # MIAO TONE ABOVE -> MIAO TONE BELOW
}
TRANSLITERATIONS = {'ß': 'ss'}

# always take the first possible rotation, but accept any reverse rotation
# in order to handle different mappings seen in the wild
TEXT_CHARS = {
    # string.printable
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
    '5':  'ϛϚ5',
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

    # couple of extras
    'œ':  'ᴔ',
    'æ':  'ᴂ',
    '‽':  '⸘',
}

_FLIPPED_TEXT_CHARS = dict()
for _char, _upside_down in TEXT_CHARS.items():
    for _upside_down_char in REGEX_GRAPHEME.findall(_upside_down):
        _FLIPPED_TEXT_CHARS.setdefault(_upside_down_char, _char)

# why are there so many mathematical symbols
# this doesn't even cover all of them
SYMBOLS_SYMMETRIC = '―\0\a\b⟛⫩∕∖∤∦∫∬∭∮∯∰∲∳∻∼∽∿≀≁≈≶≷≸≹⊘⋚⋛⟋⟍⦸⧣⧥⧵⧷⧸⧹⨌⨍⨎⨏⨫⨬⩫⩬⫻⫽⦁⦂'
SYMBOLS_LEFT = '\2⁅∴⁀⛤⬟†˕꭪⊢⊤⟝⟙⍑⍕⟟⫞⫟⫧⫪‹⁽⁾∈∊∉≂≔≪≮≺⊀⊂⊄⊏⋉⊶⊰⊲⋘≥≤⌊⌈⌠〈❨❪❬❮❰❲❴⟔⟜⟣⟥' \
               '⟦⟨⟪⟬⟮⦃⦅⦇⦉⦍⦏⦑⦓⦕⦗⧀⧙⧛⧼∱⨤⫕⫷⸢⸤⸠⸌⸍⸨⸦〈《「『【〔〖〘〚﹙﹛﹝﹤（＜［｛｟｢⩤'
SYMBOLS_RIGHT = '\3⁆∵‿⛧⯂⸸˔꭫⊣⊥⟞⟘⍊⍎⫱⊦⫠⫨⫫›₎₍∋∍∌≃≕≫≯≻⊁⊃⊅⊐⋊⊷⊱⊳⋙⋜⋝⌉⌋⌡〉❩❫❭❯❱❳❵⟓⊸⟢⟤' \
                '⟧⟩⟫⟭⟯⦄⦆⦈⦊⦎⦐⦒⦔⦖⦘⧁⧘⧚⧽⨑⨦⫖⫸⸥⸣⸡⸜⸝⸩⸧〉》」』】〕〗〙〛﹚﹜﹞﹥）＞］｝｠｣⩥'

_ALL_SYMBOLS = dict()
for _char in SYMBOLS_SYMMETRIC:
    _ALL_SYMBOLS[_char] = _char
for _left, _right in zip(SYMBOLS_LEFT, SYMBOLS_RIGHT):
    assert _left not in _ALL_SYMBOLS
    _ALL_SYMBOLS[_left] = _right
    assert _right not in _ALL_SYMBOLS
    _ALL_SYMBOLS[_right] = _left

_DIACRITICS = dict()
for _char, _upside_down_char in DIACRITICS.items():
    _DIACRITICS.setdefault(_char[-1], _upside_down_char[-1])
    _DIACRITICS.setdefault(_upside_down_char[-1], _char[-1])

_FLIPPED_CHARS = set()
for _char, _upside_down in TEXT_CHARS.items():
    _FLIPPED_CHARS.update(_upside_down)
REGEX_FLIPPED_CHAR = regex.compile(f'[{regex.escape("".join(_FLIPPED_CHARS))}]+')
REGEX_TEXT = regex.compile(f'[{regex.escape(string.printable)}]+')


def is_flipped_ascii(text: str) -> bool:
    if REGEX_TEXT.fullmatch(text):
        return False
    if REGEX_FLIPPED_CHAR.fullmatch(text):
        return True

    unflipped = ''.join(REGEX_TEXT.findall(text))
    flipped = ''.join(REGEX_FLIPPED_CHAR.findall(text))

    return len(flipped) > len(unflipped)


def flip_text(text: str) -> str:
    for _from, _to in TRANSLITERATIONS.items():
        text = text.replace(_from, _to)

    if is_flipped_ascii(text):
        char_maps = [_FLIPPED_TEXT_CHARS, TEXT_CHARS, _ALL_SYMBOLS]
    else:
        char_maps = [TEXT_CHARS, _FLIPPED_TEXT_CHARS, _ALL_SYMBOLS]

    out = []
    flipped_grapheme = []
    for grapheme in REGEX_GRAPHEME.findall(text):
        for char_map in char_maps:
            if grapheme[0] in char_map:
                flipped_grapheme.append(char_map[grapheme[0]][0])
                break
        else:
            grapheme = unicodedata.normalize('NFKD', grapheme)  # breaks some things
            for char_map in char_maps:
                if grapheme[0] in char_map:
                    flipped_grapheme.append(char_map[grapheme[0]][0])
                    break
            else:
                flipped_grapheme.append('\uFFFD')

        for diacritic in grapheme[1:]:
            if diacritic in _DIACRITICS:
                flipped_grapheme.append(_DIACRITICS[diacritic])

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
        elif REGEX_WORD_CHAR.match(token) is None:
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


def build_diacritics():
    above = dict()
    below = dict()

    with warnings.catch_warnings():
        warnings.simplefilter('ignore')

        for codepoint in range(0x10FFFF):
            diacritic = chr(codepoint)

            # just want the diacritics
            if unicodedata.category(diacritic) != 'Mn':
                continue

            try:
                name = unicodedata.name(diacritic)
            except ValueError:
                continue

            if 'OVERLAY' in name:
                below[name] = '◌' + diacritic
                above[name] = '◌' + diacritic
            elif 'OVERLINE' in name:
                above[name] = '◌' + diacritic
            elif 'LOW LINE' in name:
                name = name.replace('LOW LINE', 'OVERLINE')
                below[name] = '◌' + diacritic
            elif 'BELOW' in name:
                name = ' '.join(name.replace('BELOW', ' ').split())
                below[name] = '◌' + diacritic
            else:
                name = ' '.join(name.replace('ABOVE', ' ').split())
                above[name] = '◌' + diacritic

    def swap(_name, x, y):
        _name = _name.replace(x, '\0')
        _name = _name.replace(y, x)
        _name = _name.replace('\0', y)
        return _name

    print('DIACRITICS = {')
    for name, above_char in above.items():
        # reverse some things
        name = swap(name, 'LEFT ', 'RIGHT ')
        name = swap(name, 'UP ', 'DOWN ')
        name = swap(name, 'CIRCUMFLEX ACCENT', 'CARON')
        name = swap(name, 'INVERTED BREVE', 'BREVE')
        name = swap(name, 'INVERTED BRIDGE', 'BRIDGE')

        if name in below:
            print(f'    "{above_char}": "{below[name]}",  '
                  f'# {unicodedata.name(above_char[-1])} -> {unicodedata.name(below[name][-1])}')
    print('}')


if __name__ == '__main__':
    for char, upside_down in TEXT_CHARS.items():
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
        '''~{|}`‾^[\\]@¿<=>;:/.-ʻ+*()╻\⅋%$#﮼¡ Z⅄XϺɅՈꓕSꓤꝹԀONꟽ⅂ꓘᒋIH⅁ᖵƎᗡϽꓭ∀zʎxʍʌnʇsɹbdouɯʅʞɾᴉɥƃⅎǝpɔqɐ 68𝘓95ߤ↋↊⇂0'''))

    print(unflip_upside_down_words('normal_pꞁɹoʍ‾oꞁꞁǝɥ_text  NORMAL ᗡꞀᴚOϺ OꞀꞀƎH TEXT  normal pꞁɹoʍ oꞁꞁǝɥ text  ʇsǝʇ '))

    print(flip_text('köln'))


    print(flip_text('''[rapid] 2022-12-20 12:00:00
Keycloak: 12/12 checks are up
RAPID: 12/12 checks are up
Scoold: 1/1 checks are up'''))