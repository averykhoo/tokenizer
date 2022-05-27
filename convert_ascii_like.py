import json
import string
import warnings
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

            # add codepoints for latin-like scripts, but skip cyrillic since that's a bit different
            if any(lang in unicodedata.name(char) for lang in ('LATIN', 'GREEK', 'ROMAN', 'MODIFIER', 'MATHEMATICAL')):
                alpha_alike_codepoints[alpha].append(codepoint)

    return {codepoint: char for char, codepoints in alpha_alike_codepoints.items() for codepoint in codepoints}


def convert_ascii_alike(text: str) -> str:
    """
    Convert a string of characters that look like ASCII to a string of actual ASCII
    """
    return text.translate(get_ascii_alike_chars())


if __name__ == '__main__':
    print(json.dumps(convert_ascii_alike('𝐇𝐞𝐥𝐥𝐨 𝐖𝐨𝐫𝐥𝐝')))
    print(json.dumps(convert_ascii_alike('𝗛𝗲𝗹𝗹𝗼 𝗪𝗼𝗿𝗹𝗱')))
    print(json.dumps(convert_ascii_alike('𝐻𝑒𝑙𝑙𝑜 𝑊𝑜𝑟𝑙𝑑')))
    print(json.dumps(convert_ascii_alike('𝘏𝘦𝘭𝘭𝘰 𝘞𝘰𝘳𝘭𝘥')))
    print(json.dumps(convert_ascii_alike('𝑯𝒆𝒍𝒍𝒐 𝑾𝒐𝒓𝒍𝒅')))
    print(json.dumps(convert_ascii_alike('𝙃𝙚𝙡𝙡𝙤 𝙒𝙤𝙧𝙡𝙙')))

