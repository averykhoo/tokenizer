import unicodedata

# refer to: https://en.wikipedia.org/wiki/Whitespace_character
UNICODE_SPACES = {
    # unicode whitespace
    '\u0009',  # horizontal tab == '\t'
    '\u000a',  # line feed (new line) == '\n'
    '\u000b',  # vertical tab == '\v'
    '\u000c',  # form feed (new page) == '\f'
    '\u000d',  # carriage return == '\r'
    '\u0020',  # space == ' '
    '\u0085',  # next line
    '\u00a0',  # non-breaking space (alt+0160)
    '\u1680',  # ogham space
    '\u2000',  # en quad
    '\u2001',  # em quad
    '\u2002',  # en space
    '\u2003',  # em space
    '\u2004',  # 3-per-em space
    '\u2005',  # 4-per-em space
    '\u2006',  # 6-per-em space
    '\u2007',  # figure space
    '\u2008',  # punctuation space
    '\u2009',  # thin space
    '\u200a',  # hair space
    '\u2028',  # line separator
    '\u2029',  # paragraph separator
    '\u202f',  # narrow non-breaking space
    '\u205f',  # medium mathematical space
    '\u3000',  # ideographic space

    # technically not whitespace, but they are blank and usage of these characters is a bug
    '\u001c',  # file separator
    '\u001d',  # group separator
    '\u001e',  # record separator
    '\u001f',  # unit separator

    # technically not whitespace, but render as blank
    '\u180e',  # mongolian vowel separator (NOT WHITESPACE)
    '\u200b',  # zero width space (NOT WHITESPACE)
    '\u200c',  # zero width non-joiner (NOT WHITESPACE)
    '\u200d',  # zero width joiner (NOT WHITESPACE) (splitting on this will break some emoji!)
    '\u2060',  # word joiner (NOT WHITESPACE)
    '\ufeff',  # zero width non-breaking space (also byte order mark) (NOT WHITESPACE)

    # # unicode space-illustrating characters (visible and NOT WHITESPACE)
    # '\u00b7',  # middle dot (non-blank symbol used to represent whitespace)
    # '\u273d',  # shouldered open box (non-blank symbol used to represent whitespace)
    # '\u2420',  # symbol for space (non-blank symbol used to represent whitespace)
    # '\u2422',  # blank open symbol (non-blank symbol used to represent whitespace)
    # '\u2423',  # open box (non-blank symbol used to represent whitespace)

    # specifically defined not to be whitespace, but also blank
    '\u2800',  # braille blank (NOT WHITESPACE)
}


class _IsTextChar(dict):
    def __missing__(self, char):
        ret = self[char] = unicodedata.category(char) in {'Lu', 'Ll', 'Lt', 'Lm', 'Lo',
                                                          'Nd', 'Nl', 'No',
                                                          'Co',
                                                          }
        return ret


class _IsPunctuationChar(dict):
    def __missing__(self, char):
        ret = self[char] = unicodedata.category(char) in {'Pc', 'Pd', 'Ps', 'Pe', 'Pi', 'Pf', 'Po',
                                                          'Sm', 'Sc', 'Sk', 'So',
                                                          }
        return ret


class _IsSpaceChar(dict):
    def __missing__(self, char):
        ret = self[char] = char in UNICODE_SPACES
        return ret


_is_text_char = _IsTextChar().__getitem__  # new item for each tokenizer
_is_punctuation_char = _IsPunctuationChar().__getitem__  # new item for each tokenizer
_is_space_char = _IsSpaceChar().__getitem__  # new item for each tokenizer


def unicode61_tokenize(text, yield_non_words=True):
    text_buffer = []
    for char in text:
        # part of word, append
        if _is_text_char(char):
            text_buffer.append(char)

        # not part of word, return last word
        elif text_buffer:
            yield ''.join(text_buffer)
            text_buffer = []

            # yield non-word?
            if yield_non_words:
                yield char

        # yield non-word
        elif yield_non_words:
            yield char

    # yield remainder
    if text_buffer:
        yield ''.join(text_buffer)
