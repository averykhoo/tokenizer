import string

import unicodedata

ALPHABET = set(string.ascii_lowercase + string.ascii_uppercase)
DIGITS = set(string.digits)

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

UNPRINTABLE_CHARS = {
    '\u0000',  # null
    '\u0001',  # start of heading
    '\u0002',  # start of text
    '\u0003',  # end of text
    '\u0004',  # end of transmission
    '\u0005',  # enquiry
    '\u0006',  # acknowledge (ACK)
    '\u0007',  # bell (also used as bullet point)
    '\u0008',  # backspace
    '\u000e',  # shift out
    '\u000f',  # shift in
    '\u0010',  # data link escape
    '\u0011',  # device control 1
    '\u0012',  # device control 2
    '\u0013',  # device control 3
    '\u0014',  # device control 4
    '\u0015',  # negative acknowledge
    '\u0016',  # synchronous idle
    '\u0017',  # end of transmission block
    '\u0018',  # cancel
    '\u0019',  # end of medium
    '\u001a',  # substitute
    '\u001b',  # escape (ESC)
    '\u007f',  # delete (DEL)
    '\uffef',  # unicode invalid char (should never exist)
    '\ufffd',  # unicode replacement char
}


class _IsTextChar(dict):
    def __missing__(self, char):
        ret = self[char] = unicodedata.category(char) in {'Lu', 'Ll', 'Lt', 'Lm', 'Lo',  # letters
                                                          'Nd', 'Nl', 'No',  # numbers
                                                          'Mn', 'Mc', 'Me',  # diacritics, etc
                                                          'Co',  # private use char class
                                                          }
        return ret


class _IsPunctuationChar(dict):
    def __missing__(self, char):
        if char in UNPRINTABLE_CHARS:
            ret = self[char] = True
        else:
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


def unicode_tokenize(text, non_text_tokens=True):
    """

    :param text: string to be tokenizes
    :param non_text_tokens: whether or not to return punctuation/symbols/unprintable/whitespace
    """
    text_buffer = []
    last_space = None
    for char in text:
        # char is part of word
        if _is_text_char(char):
            # buffer contains space
            if last_space is not None:
                if non_text_tokens:
                    yield ''.join(text_buffer)
                last_space = None
                text_buffer = [char]
            # buffer contains word / is empty
            else:
                text_buffer.append(char)

        # char is space
        elif _is_space_char(char):
            # buffer contains space
            if last_space is not None:
                if last_space == char:
                    text_buffer.append(char)
                elif non_text_tokens:
                    yield ''.join(text_buffer)
                    last_space = char
                    text_buffer = [char]
                else:
                    last_space = char
                    text_buffer = [char]
            # buffer contains word
            elif text_buffer:
                yield ''.join(text_buffer)
                last_space = char
                text_buffer = [char]
            # buffer is empty
            else:
                last_space = char
                text_buffer = [char]

        # char is punctuation/symbols/unprintable AND buffer is space
        elif last_space:
            if non_text_tokens:
                yield ''.join(text_buffer)
            last_space = None
            text_buffer = []

        # char is punctuation/symbols/unprintable AND buffer is text
        elif text_buffer:
            yield ''.join(text_buffer)
            text_buffer = []

            # yield non-word?
            if non_text_tokens:
                yield char

        # char is punctuation/symbols/unprintable
        elif non_text_tokens:
            yield char

    # yield remainder
    if text_buffer:
        yield ''.join(text_buffer)


def char_group_tokenize(text, token_max_len=65535):
    """
    unused function
    tokenizes alphabet, numbers, and other unicode separately
    about 10% slower than the simpler tokenizer

    :param text:
    :param token_max_len:
    """
    # character classes

    # init
    is_space = ''
    is_num = False
    is_alpha = False
    temp = ''

    # main loop over all text
    for char in text:

        # 1) chunks of ASCII alphabets (most common case first)
        if char in ALPHABET:
            if is_alpha and len(temp) < token_max_len:
                temp += char
            else:
                if temp:
                    yield temp
                temp = char
                is_space = ''
                is_alpha = True
                is_num = False

        # 2) numbers tokenized as chunks of ASCII digits
        elif char in DIGITS:
            if is_num and len(temp) < token_max_len:
                temp += char
            else:
                if temp:
                    yield temp
                temp = char
                is_space = ''
                is_alpha = False
                is_num = True

        # 3) spaces tokenized in groups of the same char
        elif _is_space_char(char):
            if char == is_space and len(temp) < token_max_len:
                temp += char
            else:
                if temp:
                    yield temp
                temp = is_space = char
                is_alpha = False
                is_num = False

        # 4) punctuation tokenized as individual chars
        elif _is_punctuation_char(char):
            if temp:
                yield temp
            yield char
            temp = is_space = ''
            is_alpha = False
            is_num = False

        # 5) arbitrary unicode, first token
        elif is_space or is_num or is_alpha:
            if temp:
                yield temp
            temp = char
            is_space = ''
            is_num = False
            is_alpha = False

        # 6) arbitrary unicode, next token
        elif len(temp) < token_max_len:
            temp += char

        # 7) arbitrary unicode, max token
        else:
            yield temp
            temp = char

    # finally, yield the last chunk
    if temp:
        yield temp
