import json
import string
import warnings
from collections import Counter
from functools import lru_cache
from typing import Dict

import ftfy as ftfy
import unicodedata
import unidecode
# noinspection PyUnresolvedReferences
from bs4 import UnicodeDammit


def fix_unicode(text: str) -> str:
    """
    Fix unicode text

    :param text:
    :return:
    """

    # decode bytes
    if isinstance(text, (bytes, bytearray)):
        text = UnicodeDammit.detwingle(text)

    # unexpected type, just coerce
    elif not isinstance(text, str):
        text = str(text)

    # convert to unicode
    text = UnicodeDammit(text).unicode_markup

    # ftfy for good measure
    text = ftfy.fix_text(text)

    # todo: set flags for suggested encoding, fixing quotation marks, etc
    text = UnicodeDammit(text,
                         smart_quotes_to='ascii',
                         # user_encodings=['utf8', 'utf16'],
                         ).unicode_markup

    return unicodedata.normalize('NFKD', text)


@lru_cache
def get_ascii_alike_chars() -> Dict[int, str]:
    """
    Return a string of characters that look like ASCII
    """
    alpha_alike_codepoints = dict()
    for char in string.ascii_letters + string.digits:
        alpha_alike_codepoints[char] = []

    with warnings.catch_warnings():
        warnings.simplefilter('ignore')

        c = Counter()
        for codepoint in range(0x10FFFF):
            char = chr(codepoint)

            # ignore the ascii letters themselves
            if char in alpha_alike_codepoints:
                continue

            # skip chars that aren't text chars
            if unicodedata.category(char)[0] != 'L' and unicodedata.category(char) not in {'So', 'No'}:
                continue

            # unidecode is usually good at getting the ascii-like char, but adds brackets to symbol-like chars
            alpha = unidecode.unidecode(char)
            if alpha.startswith('(') and alpha.endswith(')'):
                alpha = alpha[1:-1]  # e.g. '🅤' -> '(U)'
            if alpha.startswith('[') and alpha.endswith(']'):
                alpha = alpha[1:-1]  # e.g. '🆄' -> '[U]'
            if alpha.startswith('<') and alpha.endswith('>'):
                alpha = alpha[1:-1]  # e.g. '🄪' -> '<S>'

            # this may break some emoji, but sometimes people use it as letters
            try:
                if not alpha and unicodedata.name(char).startswith('REGIONAL INDICATOR SYMBOL LETTER'):
                    alpha = unicodedata.name(char)[32:].strip()
            except ValueError:
                pass

            # we're only looking for chars that map to ascii letters
            if alpha not in alpha_alike_codepoints:
                continue

            # add codepoints for latin-like scripts, but skip armenian/cyrillic since that's a bit different
            if ((alpha in string.ascii_letters and
                 any(lang in unicodedata.name(char) for lang in (
                         'LATIN', 'GREEK', 'ROMAN', 'MODIFIER',
                         'MATHEMATICAL', 'DOUBLE-STRUCK', 'SCRIPT SMALL',
                         'SCRIPT CAPITAL', 'BLACK-LETTER',
                         'REGIONAL INDICATOR', 'SUBSCRIPT', 'SUPERSCRIPT',
                         'TURNED', 'TORTOISE SHELL',
                         'COPYRIGHT SIGN', 'REGISTERED SIGN',
                         'FEMININE ORDINAL INDICATOR',
                         'MASCULINE ORDINAL INDICATOR', 'KELVIN SIGN',
                         'PLANCK CONSTANT', 'ANGSTROM SIGN', 'ESTIMATED SYMBOL',
                         'INFORMATION SOURCE', 'TONE FIVE', 'MICRO SIGN', 'SOUND RECORDING COPYRIGHT')) and
                 all(lang not in unicodedata.name(char) for lang in (
                         'LETTER PHI', 'LETTER ETA', 'LETTER OMEGA', 'LETTER PI', 'LETTER XI', 'LETTER ZETA',
                         'LETTER KOPPA',
                         'GREEK PHI', 'GREEK PI',
                         'LETTER WYNN', 'LETTER YOGH'))
            ) or (
                    alpha in string.digits and
                    any(lang in unicodedata.name(char) for lang in ('DIGIT', 'SUBSCRIPT', 'SUPERSCRIPT')) and
                    'ETHIOPIC' not in unicodedata.name(char))):
                alpha_alike_codepoints[alpha].append(codepoint)
                # print(chr(codepoint), f'U+{codepoint:04x}', unicodedata.name(char))
            else:
                c.update(unicodedata.name(char).split())
                print(char, unicodedata.name(char), alpha)

    # print(c.most_common(100))
    # print({chr(codepoint): char for char, codepoints in alpha_alike_codepoints.items() for codepoint in codepoints})
    return {codepoint: char for char, codepoints in alpha_alike_codepoints.items() for codepoint in codepoints}


def normalize_unicode(text: str) -> str:
    """
    normalize unicode characters that to ASCII characters
    """
    text = fix_unicode(text)

    # copilot suggested this
    text = text.replace(u'\u2013', '-')
    text = text.replace(u'\u2014', '-')
    text = text.replace(u'\u2018', "'")
    text = text.replace(u'\u2019', "'")
    text = text.replace(u'\u201a', ',')
    text = text.replace(u'\u201b', '"')
    text = text.replace(u'\u201c', '"')
    text = text.replace(u'\u201d', '"')
    text = text.replace(u'\u201e', '"')
    text = text.replace(u'\u201f', '"')
    text = text.replace(u'\u2022', '*')
    text = text.replace(u'\u2026', '...')
    text = text.replace(u'\u00a0', ' ')
    text = text.replace(u'\u20ac', '€')

    # zero-width stuff
    text = text.replace(u'\u200b', '')
    text = text.replace(u'\u200c', '')
    text = text.replace(u'\u200d', '')
    text = text.replace(u'\ufeff', '')

    return text.translate(get_ascii_alike_chars())


if __name__ == '__main__':
    print(json.dumps(normalize_unicode('𝐇𝐞𝐥𝐥𝐨 𝐖𝐨𝐫𝐥𝐝')))
    print(json.dumps(normalize_unicode('𝗛𝗲𝗹𝗹𝗼 𝗪𝗼𝗿𝗹𝗱')))
    print(json.dumps(normalize_unicode('𝐻𝑒𝑙𝑙𝑜 𝑊𝑜𝑟𝑙𝑑')))
    print(json.dumps(normalize_unicode('𝘏𝘦𝘭𝘭𝘰 𝘞𝘰𝘳𝘭𝘥')))
    print(json.dumps(normalize_unicode('𝑯𝒆𝒍𝒍𝒐 𝑾𝒐𝒓𝒍𝒅')))
    print(json.dumps(normalize_unicode('𝙃𝙚𝙡𝙡𝙤 𝙒𝙤𝙧𝙡𝙙')))
    print(json.dumps(normalize_unicode('Ｕｎｉｃｏｄｅ!')))
    print(json.dumps(normalize_unicode('🅤🅝🅘🅒🅞🅓🅔‽')))
    print(json.dumps(normalize_unicode('🇺‌🇳‌🇮‌🇨‌🇴‌🇩‌🇪!')))

    from pprint import pprint

    groupby = {}
    for o, c in get_ascii_alike_chars().items():
        groupby.setdefault(c, []).append(chr(o))
    pprint({alpha: ''.join(sorted(groupby[alpha])) for alpha in sorted(groupby.keys())})
