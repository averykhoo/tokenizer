from collections import namedtuple
from enum import Enum
from enum import auto
from typing import Any
from typing import Generator
from typing import List
from typing import Tuple
from typing import Union

import unicodedata


class TokenCategory(Enum):
    WORD = auto()
    WHITESPACE = auto()
    PUNCTUATION = auto()


Token = namedtuple('Token', ['text', 'start_pos', 'category'])

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
    # ':',
    '?',
    '\u00a1',  # upside down -> '¡'
    '\u00bf',  # upside down -> '¿'
    '\u0589',  # armenian full stop -> '։'
    '\u06d4',  # arabic full stop = -> '۔'
    '\u2026',  # ellipsis -> '…'
    '\u203c',  # double -> '‼'
    '\u203d',  # interrobang -> '‽'
    '\u2047',  # double -> '⁇'
    '\u2048',  # double -> '⁈'
    '\u2049',  # double -> '⁉'
    '\u3002',  # chinese -> '。'
    '\ufe12',  # chinese presentation form -> '︒'
    '\ufe15',  # presentation form -> '︕'
    '\ufe16',  # presentation form -> '︖'
    '\ufe52',  # small form -> '﹒'
    # '\ufe55',  # small form -> '﹕'
    '\ufe56',  # small form -> '﹖'
    '\ufe57',  # small form -> '﹗'
    '\uff01',  # full width -> '！'
    '\uff0e',  # full width -> '．'
    # '\uff1a',  # full width -> '：'
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


def _unicode_tokenize_all_strings(text: str) -> Generator[str, Any, None]:
    word_buffer = []
    for idx, char in enumerate(text):
        # char is part of word
        if is_text_char(char):
            word_buffer.append(char)

        # char is whitespace/punctuation/symbol/unprintable
        else:
            if word_buffer:
                yield ''.join(word_buffer)
                word_buffer = []

            yield char

    # yield remainder
    if word_buffer:
        yield ''.join(word_buffer)


def _unicode_tokenize_all_tokens(text: str) -> Generator[Token, Any, None]:
    word_buffer = []
    start_idx = None
    for idx, char in enumerate(text):
        # char is part of word
        if is_text_char(char):
            # buffer is empty
            if not word_buffer:
                word_buffer = [char]
                start_idx = idx
            # buffer contains word
            else:
                word_buffer.append(char)

        # char is whitespace
        elif is_space_char(char):
            if word_buffer:
                yield Token(''.join(word_buffer), start_idx, TokenCategory.WORD)
                word_buffer = []

            yield Token(char, idx, TokenCategory.WHITESPACE)

        # char is punctuation/symbol/unprintable
        else:
            if word_buffer:
                yield Token(''.join(word_buffer), start_idx, TokenCategory.WORD)
                word_buffer = []

            yield Token(char, idx, TokenCategory.PUNCTUATION)

    # yield remainder
    if word_buffer:
        yield Token(''.join(word_buffer), start_idx, TokenCategory.WORD)


def _unicode_tokenize_word_strings(text: str) -> Generator[str, Any, None]:
    word_buffer = []
    for char in text:
        # char is part of word
        if is_text_char(char):
            word_buffer.append(char)

        # char is non-text AND buffer is text
        elif word_buffer:
            yield ''.join(word_buffer)
            word_buffer = []

    # yield remainder
    if word_buffer:
        yield ''.join(word_buffer)


def _unicode_tokenize_word_tokens(text: str) -> Generator[Token, Any, None]:
    word_buffer = []
    start_idx = None
    for idx, char in enumerate(text):
        # char is part of word
        if is_text_char(char):
            if not word_buffer:
                word_buffer = [char]
                start_idx = idx
            else:
                word_buffer.append(char)

        # char is non-text AND buffer is text
        elif word_buffer:
            yield Token(''.join(word_buffer), start_idx, TokenCategory.WORD)
            word_buffer = []

    # yield remainder
    if word_buffer:
        yield Token(''.join(word_buffer), start_idx, TokenCategory.WORD)


def unicode_tokenize(text: str,
                     words_only: bool = False,
                     as_tokens: bool = False
                     ) -> Generator[Union[str, Token], Any, None]:
    """
    similar to fts5's unicode61 tokenizer, but allows diacritics

    :param text: string to be tokenized
    :param words_only: whether or not to return punctuation/symbols/unprintable/whitespace
    :param as_tokens: return as Token namedtuple (includes start_position and token_category)
    """

    if as_tokens and words_only:
        return _unicode_tokenize_word_tokens(text)

    elif as_tokens:
        return _unicode_tokenize_all_tokens(text)  # use `_unicode_tokenize_merge_spaces` if you want to merge spaces

    elif words_only:
        return _unicode_tokenize_word_strings(text)

    else:
        return _unicode_tokenize_all_strings(text)


def sentence_split_tokens(text: str, split_newline: Union[str, bool] = True) -> Generator[List[Token], Any, None]:
    """
    good-enough sentence splitting
    optional splitting on newlines to ensure sentences don't span paragraphs
    split_newline can be a string on which to split (e.g. '\r\n\r\n')

    :param text: to split in sentences
    :param split_newline: split paragraphs before sentence splitting
    :param words_only: don't return non-word tokens
    :return: list of Token objects
    """
    token: Token

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
        for token in unicode_tokenize(para, as_tokens=True):
            buffer.append(token)

            # sentence has ended iff whitespace follows the closing punctuation
            if closed and token.category is TokenCategory.WHITESPACE:
                if buffer:
                    yield buffer
                buffer = []
                closed = False
                continue

            # note that this can also un-close a sentence, e.g. for "192.168.1.1"
            if token.text not in {'"', '\uff02',
                                  ')', '\uff09',
                                  '>', '\uff1e',
                                  ']', '\uff3d',
                                  '}', '\uff5d',
                                  '\u201d'}:
                closed = token.text in CLOSING_PUNCTUATION

        if buffer:
            yield buffer


def sentence_split(text: str, split_newline: Union[str, bool] = True) -> Generator[str, Any, None]:
    for sentence_tokens in sentence_split_tokens(text, split_newline=split_newline):
        sentence = ''.join(token.text for token in sentence_tokens).strip()
        if sentence:
            yield sentence


def word_n_grams(text: str, n: int = 2, split_sentences: bool = True) -> Generator[Tuple[str, str], Any, None]:
    """
    yield n-grams of words (works ONLY for space-delimited languages)
    note that split_sentences will also split paragraphs by default
    WARNING: if there are less than N tokens, no n-grams will be returned for the sentence

    :param text:
    :param n:
    :param split_sentences:
    :return:
    """
    # if n == 1, you're using the wrong function
    assert n >= 2

    if split_sentences:
        for sentence_tokens in sentence_split_tokens(text):
            words = [token.text for token in sentence_tokens if token.category is TokenCategory.WORD]
            for n_gram in zip(*[words[i:] for i in range(n)]):
                yield n_gram

    else:
        words = list(unicode_tokenize(text, words_only=True))
        for n_gram in zip(*[words[i:] for i in range(n)]):
            yield n_gram
