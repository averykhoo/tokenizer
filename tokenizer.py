from collections import namedtuple
from enum import Enum
from enum import auto
from typing import Any
from typing import Generator
from typing import Tuple
from typing import Union

import unicodedata

UNICODE_SPACES = {  # refer to: https://en.wikipedia.org/wiki/Whitespace_character
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

CLOSING_PUNCTUATION = {
    '!',
    '.',
    ':',
    '?',
    '\u00a1',  # upside down -> '¡'
    '\u00bf',  # upside down -> '¿'
    '\u0589',  # armenian full stop -> '։'
    '\u06d4',  # arabic full stop = -> '۔'
    '\u2026',  # ellipsis -> '…'
    '\u203c',  # double -> '‼'
    '\u2047',  # double -> '⁇'
    '\u2048',  # double -> '⁈'
    '\u2049',  # double -> '⁉'
    '\u3002',  # chinese -> '。'
    '\ufe12',  # chinese presentation form -> '︒'
    '\ufe15',  # presentation form -> '︕'
    '\ufe16',  # presentation form -> '︖'
    '\ufe52',  # small form -> '﹒'
    '\ufe55',  # small form -> '﹕'
    '\ufe56',  # small form -> '﹖'
    '\ufe57',  # small form -> '﹗'
    '\uff01',  # full width -> '！'
    '\uff0e',  # full width -> '．'
    '\uff1a',  # full width -> '：'
    '\uff1f',  # full width -> '？'
    '\uff61',  # half width chinese -> '｡'
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


is_text_char = _IsTextChar().__getitem__  # new item for each tokenizer
is_punctuation_char = _IsPunctuationChar().__getitem__  # new item for each tokenizer
is_space_char = _IsSpaceChar().__getitem__  # new item for each tokenizer


class TokenCategory(Enum):
    WORD = auto()
    WHITESPACE = auto()
    PUNCTUATION = auto()


Token = namedtuple('Token', ['text', 'start_pos', 'category'])


def _unicode_tokenize_all(text):
    text_buffer = []  # stores chars for previous whitespace/word sequence
    start_idx = None
    category = None
    for idx, char in enumerate(text):
        # char is part of word
        if is_text_char(char):
            # buffer is empty
            if not text_buffer:
                text_buffer = [char]
                start_idx = idx
                category = TokenCategory.WORD
            # buffer contains word
            elif category is TokenCategory.WORD:
                text_buffer.append(char)
            # buffer contains space
            else:
                yield ''.join(text_buffer), start_idx, category
                text_buffer = [char]
                start_idx = idx
                category = TokenCategory.WORD

        # char is space
        elif is_space_char(char):
            # buffer is empty
            if not text_buffer:
                text_buffer = [char]
                start_idx = idx
                category = TokenCategory.WHITESPACE
            # buffer contains word
            elif category is TokenCategory.WORD:
                yield ''.join(text_buffer), start_idx, category
                text_buffer = [char]
                start_idx = idx
                category = TokenCategory.WHITESPACE
            # buffer contains same space
            elif text_buffer[-1] == char:
                text_buffer.append(char)
            # buffer contains different space
            else:  # category is already WHITESPACE, don't need to set again
                yield ''.join(text_buffer), start_idx, category
                text_buffer = [char]
                start_idx = idx

        # char is punctuation/symbol/unprintable
        else:
            # buffer is text or whitespace
            if text_buffer:
                yield ''.join(text_buffer), start_idx, category
                text_buffer = []

            yield char, idx, TokenCategory.PUNCTUATION

    # yield remainder
    if text_buffer:
        yield ''.join(text_buffer), start_idx, category


def _unicode_tokenize_words(text):
    text_buffer = []
    start_idx = None
    for idx, char in enumerate(text):
        # char is part of word
        if is_text_char(char):
            if not text_buffer:
                text_buffer = [char]
                start_idx = idx
            else:
                text_buffer.append(char)

        # char is non-text AND buffer is text
        elif text_buffer:
            yield ''.join(text_buffer), start_idx, TokenCategory.WORD
            text_buffer = []

    # yield remainder
    if text_buffer:
        yield ''.join(text_buffer), start_idx, TokenCategory.WORD


def unicode_tokenize(text: str, words_only: bool = False, as_tokens=False) -> Generator[Union[str, Token], Any, None]:
    """
    similar to fts5's unicode61 tokenizer, but merges spaces and allows diacritics

    :param text: string to be tokenized
    :param words_only: whether or not to return punctuation/symbols/unprintable/whitespace
    :param as_tokens: return as Token namedtuple (includes start_position and token_category)
    """
    if words_only:
        _tokenizer = _unicode_tokenize_words
    else:
        _tokenizer = _unicode_tokenize_all

    if as_tokens:
        for token, start_idx, category in _tokenizer(text):
            yield Token(token, start_idx, category)
    else:
        for token, *_ in _tokenizer(text):
            yield token


def sentence_split(text: str, split_newline: Union[str, bool, None] = True) -> Generator[str, Any, None]:
    """
    good-enough sentence splitting
    optional splitting on newlines to ensure sentences don't span paragraphs
    split_newline can be a string on which to split (e.g. '\r\n\r\n')

    :param text: to split in sentences
    :param split_newline: split paragraphs before sentence splitting
    :return:
    """
    if split_newline is True:
        paragraphs = [para.strip() for para in text.split('\n')]
    elif split_newline:
        assert isinstance(split_newline, str)
        paragraphs = [para.strip() for para in text.split(split_newline)]
    else:
        paragraphs = [text.strip()]

    for para in paragraphs:
        buffer = []
        closed = False
        for token in unicode_tokenize(para):
            buffer.append(token)

            if closed and is_space_char(token[0]):
                sentence = ''.join(buffer).strip()
                if sentence:
                    yield sentence
                buffer = []
                closed = False
                continue

            if token not in {'"', '\uff02', ')', '\uff09', '>', '\uff1e', ']', '\uff3d', '}', '\uff5d', '\u201d'}:
                closed = token in CLOSING_PUNCTUATION

        sentence = ''.join(buffer).strip()
        if sentence:
            yield sentence


def word_n_grams(text: str, n: int = 2, split_sentences: bool = True) -> Generator[Tuple[str, str], Any, None]:
    """
    yield n-grams of words (works ONLY for space-delimited languages)
    note that split_sentences will also split paragraphs by default

    :param text:
    :param n:
    :param split_sentences:
    :return:
    """
    if split_sentences:
        sentences = list(sentence_split(text))
    else:
        sentences = [text]

    for sentence in sentences:
        words = list(unicode_tokenize(sentence, words_only=True))
        for n_gram in zip(*[words[i:] for i in range(n)]):
            yield n_gram
