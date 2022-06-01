import json
import string
import warnings
from collections import Counter
from functools import lru_cache
from typing import Dict

import unicodedata
import unidecode


@lru_cache
def get_ascii_alike_chars() -> Dict[int, str]:
    """
    Return a string of characters that look like ASCII
    """
    alpha_alike_codepoints = dict()
    for char in string.ascii_letters:
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
            if unicodedata.category(char)[0] != 'L':
                continue

            # we're only looking for chars that map to ascii letters
            alpha = unidecode.unidecode(char)
            if alpha not in alpha_alike_codepoints:
                continue

            # add codepoints for latin-like scripts, but skip armenian/cyrillic since that's a bit different
            if any(lang in unicodedata.name(char) for lang in ('LATIN', 'GREEK', 'ROMAN', 'MODIFIER',
                                                               'MATHEMATICAL', 'DOUBLE-STRUCK', 'SCRIPT SMALL',
                                                               'SCRIPT CAPITAL', 'BLACK-LETTER')):
                alpha_alike_codepoints[alpha].append(codepoint)
                # print(chr(codepoint), f'U+{codepoint:04x}', unicodedata.name(char))
            else:
                c.update(unicodedata.name(char).split())

    # print(c.most_common(100))
    # print({chr(codepoint): char for char, codepoints in alpha_alike_codepoints.items() for codepoint in codepoints})
    return {codepoint: char for char, codepoints in alpha_alike_codepoints.items() for codepoint in codepoints}


def convert_ascii_alike(text: str) -> str:
    """
    Convert a string of characters that look like ASCII to a string of actual ASCII
    
    todo: try out some unicode fixing
    
    # decode bytes
    if isinstance(text, (bytes, bytearray)):
        text = UnicodeDammit.detwingle(text)

    # unexpected type, just coerce
    elif not isinstance(text, str):
        text = str(text)

    # convert to unicode
    text = UnicodeDammit(text, most_likely_encodings).unicode_markup

    # ftfy for good measure
    return ftfy.fix_text(text)
    """
    return text.translate(get_ascii_alike_chars())


if __name__ == '__main__':
    print(json.dumps(convert_ascii_alike('𝐇𝐞𝐥𝐥𝐨 𝐖𝐨𝐫𝐥𝐝')))
    print(json.dumps(convert_ascii_alike('𝗛𝗲𝗹𝗹𝗼 𝗪𝗼𝗿𝗹𝗱')))
    print(json.dumps(convert_ascii_alike('𝐻𝑒𝑙𝑙𝑜 𝑊𝑜𝑟𝑙𝑑')))
    print(json.dumps(convert_ascii_alike('𝘏𝘦𝘭𝘭𝘰 𝘞𝘰𝘳𝘭𝘥')))
    print(json.dumps(convert_ascii_alike('𝑯𝒆𝒍𝒍𝒐 𝑾𝒐𝒓𝒍𝒅')))
    print(json.dumps(convert_ascii_alike('𝙃𝙚𝙡𝙡𝙤 𝙒𝙤𝙧𝙡𝙙')))
