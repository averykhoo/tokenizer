import string
import sys
from collections import defaultdict

import unicodedata

if __name__ == '__main__':

    # https://stackoverflow.com/questions/14245893/efficiently-list-all-characters-in-a-given-unicode-category

    unicode_category = defaultdict(list)
    unicode_bidirectional = defaultdict(list)
    unicode_numeric = defaultdict(list)
    unicode_digit = defaultdict(list)
    unicode_decimal = defaultdict(list)

    for c in map(chr, range(sys.maxunicode + 1)):
        unicode_category[unicodedata.category(c)].append(c)

        if unicodedata.bidirectional(c):
            unicode_bidirectional[unicodedata.bidirectional(c)].append(c)

        if unicodedata.numeric(c, None) is not None:
            unicode_numeric[unicodedata.numeric(c)].append(c)

        if unicodedata.digit(c, None) is not None:
            unicode_digit[unicodedata.digit(c)].append(c)

        if unicodedata.decimal(c, None) is not None:
            unicode_decimal[unicodedata.decimal(c)].append(c)

    # get all punctuation
    punctuation = set()
    for class_name in unicode_category.keys():
        if class_name.startswith('P') or class_name.startswith('S'):
            print(class_name)
            for char in unicode_category[class_name]:
                punctuation.add(char)

    with open('punctuation_lookup.py', 'w', encoding='ascii') as f:
        f.write('PUNCTUATION = {\n')
        for p in sorted(punctuation):

            if p == '"':
                f.write(f'    \'"\',')
            elif p == '\\':
                f.write(f'    "\\\\",')
            elif p in string.printable:
                f.write(f'    "{p}",')
            elif ord(p) <= 0xffff:
                f.write(f'    "\\u{ord(p):04x}",')
            else:
                f.write(f'    "\\U{ord(p):08x}",')

            if unicodedata.name(p, None) is not None:
                f.write(f'  # {unicodedata.name(p)}')

            f.write('\n')
        f.write('}\n')
