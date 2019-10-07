"""
given a large bunch (~1e7) of things to find and replace and a folder of data to clean
and writes the cleaned copied data to the output folder, preserving the relative path

if a tokenizer is used, only matches at token boundaries
"""
import collections
import datetime
import glob
import io
import os
import random
import re
import time

import math

try:
    from punctuation_lookup import PUNCTUATION
except ImportError:
    PUNCTUATION = {'!',
                   '"',
                   '#',
                   '$',
                   '%',
                   '&',
                   "'",
                   '(',
                   ')',
                   '*',
                   '+',
                   ',',
                   '-',
                   '.',
                   '/',
                   ':',
                   ';',
                   '<',
                   '=',
                   '>',
                   '?',
                   '@',
                   '[',
                   '\\',
                   ']',
                   '^',
                   '_',
                   '`',
                   '{',
                   '|',
                   '}',
                   '~',
                   '\u2014',  # en dash
                   '\u2013',  # em dash
                   '\u2025',
                   '\u2026',  # horizontal ellipsis
                   '\u22ee',  # vertical ellipsis
                   # '\u22ef',  # midline horizontal ellipsis
                   '\u3002',  # ideographic full stop (chinese)
                   '\u300e',  # left white corner bracket (chinese)
                   '\u300f',  # right white corner bracket (chinese)
                   '\u300c',  # left corner bracket (chinese)
                   '\u300d',  # right corner bracket (chinese)
                   '\ufe41',  # presentation form for vertical left angle bracket (chinese)
                   '\ufe42',  # presentation form for vertical right corner bracket (chinese)
                   '\u3001',  # ideographic/dun comma (chinese)
                   '\u2022',  # middle dot
                   '\u2027',  # hyphenation point
                   '\u300a',  # left double angle bracket
                   '\u300b',  # right double angle bracket
                   '\u3008',  # left angle bracket
                   '\u3009',  # right angle bracket
                   '\ufe4f',  # wavy low line
                   # '\uff5e',  # wavy dash
                   '\uff0c',  # fullwidth comma (chinese)
                   '\uff01',  # fullwidth exclamation mark (chinese)
                   '\uff1f',  # fullwidth question mark (chinese)
                   '\uff1b',  # fullwidth semicolon (chinese)
                   '\uff1a',  # fullwidth colon (chinese)
                   '\uff08',  # fullwidth left parenthesis (chinese)
                   '\uff09',  # fullwidth right parenthesis (chinese)
                   '\uff3b',  # fullwidth left square bracket (chinese)
                   '\uff3d',  # fullwidth right square bracket (chinese)
                   '\u3010',  # left black lenticular bracket (chinese)
                   '\u3011',  # right black lenticular bracket (chinese)
                   }

NUMBERS = {'1',
           '2',
           '3',
           '4',
           '5',
           '6',
           '7',
           '8',
           '9',
           '0',
           '\uff11',  # fullwidth 1
           '\uff12',  # fullwidth 2
           '\uff13',  # fullwidth 3
           '\uff14',  # fullwidth 4
           '\uff15',  # fullwidth 5
           '\uff16',  # fullwidth 6
           '\uff17',  # fullwidth 7
           '\uff18',  # fullwidth 8
           '\uff19',  # fullwidth 9
           '\uff10',  # fullwidth 0
           }

ALPHABET = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')

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
    '\u00a0',  # non-breaking space
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


def format_bytes(num):
    """
    string formatting

    :type num: int
    :rtype: str
    """
    num = abs(num)
    if num == 0:
        return '0 Bytes'
    elif num == 1:
        return '1 Byte'
    unit = 0
    while num >= 1024 and unit < 8:
        num /= 1024.0
        unit += 1
    unit = ['Bytes', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB', 'EiB', 'ZiB', 'YiB'][unit]
    return ('%.2f %s' if num % 1 else '%d %s') % (num, unit)


def format_seconds(num):
    """
    string formatting

    :type num: int | float
    :rtype: str
    """
    num = abs(num)
    if num == 0:
        return '0 seconds'
    elif num == 1:
        return '1 second'
    if num < 1:
        # display 2 significant figures worth of decimals
        return ('%%0.%df seconds' % (1 - int(math.floor(math.log10(abs(num)))))) % num
    unit = 0
    denominators = [60.0, 60.0, 24.0, 7.0]
    while num >= denominators[unit] and unit < 4:
        num /= denominators[unit]
        unit += 1
    unit = ['seconds', 'minutes', 'hours', 'days', 'weeks'][unit]
    return ('%.2f %s' if num % 1 else '%d %s') % (num, unit[:-1] if num == 1 else unit)


def char_group_tokenize(text, token_max_len=65535):
    """
    unused function
    tokenizes alphabet, numbers, and other unicode separately
    about 10% slower than the simpler tokenizer

    :param text:
    :param token_max_len:
    """
    # character classes
    punctuation = PUNCTUATION | UNPRINTABLE_CHARS
    spaces = UNICODE_SPACES
    numbers = NUMBERS
    alphabet = ALPHABET

    # init
    is_space = ''
    is_num = False
    is_alpha = False
    temp = ''

    # main loop over all text
    for char in text:

        # 1) chunks of alphabets (most common case first)
        if char in alphabet:
            if is_alpha and len(temp) < token_max_len:
                temp += char
            else:
                if temp:
                    yield temp
                temp = char
                is_space = ''
                is_alpha = True
                is_num = False

        # 2) numbers tokenized as chunks of digits
        elif char in numbers:
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
        elif char in spaces:
            if char == is_space and len(temp) < token_max_len:
                temp += char
            else:
                if temp:
                    yield temp
                temp = is_space = char
                is_alpha = False
                is_num = False

        # 4) punctuation tokenized as individual chars
        elif char in punctuation:
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


def space_tokenize(text, token_max_len=65535, emit_space=True, emit_punc=True):
    """
    tokenize by whitespace (and punctuation)

    :param text: to be split
    :param token_max_len: truncate tokens after this length
    :param emit_space: emit spaces
    :param emit_punc: emit punctuation
    """
    # character classes
    punctuation = PUNCTUATION | UNPRINTABLE_CHARS
    spaces = UNICODE_SPACES

    # init
    is_space = ''
    temp = ''

    # main loop over all text
    for char in text:
        # 1) spaces
        if char in spaces:
            if char == is_space and len(temp) < token_max_len:
                temp += char
            else:
                if temp:
                    yield temp
                temp = is_space = char if emit_space else ''

        # 2) punctuation
        elif char in punctuation:
            if temp:
                yield temp
            if emit_punc:
                yield char
            temp = is_space = ''

        # 3) first char
        elif is_space:
            if temp:
                yield temp
            temp = char
            is_space = ''

        # 4) next char
        elif len(temp) < token_max_len:
            temp += char

        # 5) max char
        else:
            yield temp
            temp = char

    # finally, yield the last chunk
    if temp:
        yield temp


def yield_lines(file_path, make_lower=False, threshold_len=0):
    """
    yields all non-empty lines in a file

    :param file_path: file to read
    :param make_lower: force line to lowercase
    :param threshold_len: ignore lines equal <= this length
    """
    with io.open(file_path, mode='rt', encoding='utf-8') as _f:
        for line in _f:
            line = line.strip()
            if make_lower:
                line = line.lower()
            if len(line) > threshold_len:
                yield line


_SENTINEL = object()


class Trie(object):
    """
    to find and replace lots of things in one pass
    something like aho-corasick search but it can do replacements
    """

    __slots__ = ('head', 'tokenizer', 'detokenizer')

    @staticmethod
    def fromkeys(keys, default='', verbose=False, case_sensitive=True):
        _trie = Trie(case_sensitive=case_sensitive)
        _trie.update(((key, default) for key in keys), verbose=verbose)
        return _trie

    class Node(dict):
        __slots__ = ('REPLACEMENT',)

        # noinspection PyMissingConstructor
        def __init__(self):
            self.REPLACEMENT = _SENTINEL

    def __init__(self, replacements=None, lexer=None, unlexer=None, case_sensitive=False):
        """

        :param replacements:
        :param lexer: tokenizer that reads one character at a time and yields tokens
        :param unlexer: function to combine tokens back into a string
        :param case_sensitive: if False, lowercase all the things (including output)
        """
        """
        :type lexer: Iterable -> Iterable
        """
        self.head = self.Node()

        if lexer is None:
            if case_sensitive:
                def _lexer(seq):
                    for elem in seq:
                        yield elem
            else:
                def _lexer(seq):
                    for elem in seq:
                        yield elem.lower()
        elif case_sensitive:
            def _lexer(seq):
                for elem in lexer(seq):
                    yield elem.lower()
        else:
            _lexer = lexer
        self.tokenizer = _lexer

        if unlexer is None:
            def unlexer(seq):
                return ''.join(seq)
        self.detokenizer = unlexer

        if replacements is not None:
            self.update(replacements)

    def __contains__(self, key):
        head = self.head
        for token in self.tokenizer(key):
            if token not in head:
                return False
            head = head[token]
        return head.REPLACEMENT is not _SENTINEL

    def _item_slice(self, start, stop, step=None):
        out = []
        for key, value in self.items():
            if key >= stop:
                return out[::step]
            elif key >= start:
                out.append((key, value))
        return out[::step]

    def __getitem__(self, key):
        if type(key) is slice:
            return [value for key, value in self._item_slice(key.start, key.stop, key.step)]
        head = self.head
        for token in self.tokenizer(key):
            if token not in head:
                raise KeyError(key)
            head = head[token]
        if head.REPLACEMENT is _SENTINEL:
            raise KeyError(key)
        return head.REPLACEMENT

    def setdefault(self, key, value):
        head = self.head
        for token in self.tokenizer(key):
            head = head.setdefault(token, self.Node())
        if head.REPLACEMENT is not _SENTINEL:
            return head.REPLACEMENT
        head.REPLACEMENT = value
        return value

    def __setitem__(self, key, value):
        head = self.head
        for token in self.tokenizer(key):
            head = head.setdefault(token, self.Node())
        head.REPLACEMENT = value
        return value

    def pop(self, key=None):
        if key is None:
            # todo: check empty trie
            for key in self.keys():
                break

        head = self.head
        breadcrumbs = [(None, head)]
        for token in self.tokenizer(key):
            head = head.setdefault(token, self.Node())
            breadcrumbs.append((token, head))
        if head.REPLACEMENT is _SENTINEL:
            raise KeyError(key)
        out = head.REPLACEMENT
        head.REPLACEMENT = _SENTINEL
        prev_token, _ = breadcrumbs.pop(-1)
        for token, head in breadcrumbs[::-1]:
            if len(head[prev_token]) == 0:
                del head[prev_token]
                prev_token = token
            else:
                break
            if head.REPLACEMENT is not _SENTINEL:
                break
        return out

    def items(self):
        _path = []
        _stack = [(self.head, sorted(self.head.keys(), reverse=True))]
        while _stack:
            head, keys = _stack.pop(-1)
            if keys:
                key = keys.pop(-1)
                _stack.append((head, keys))
                head = head[key]
                _path.append(key)
                if head.REPLACEMENT is not _SENTINEL:
                    yield ''.join(_path), head.REPLACEMENT
                _stack.append((head, sorted(head.keys(), reverse=True)))
            elif _path:
                _path.pop(-1)
            else:
                assert not _stack

    def to_regex(self, fuzzy_quotes=True, fuzzy_spaces=True, fffd_any=True, simplify=True, boundary=False):
        """
        build a (potentially very very long) regex to find any text in the trie

        :param fuzzy_quotes: unicode quotes also match ascii quotes
        :param fuzzy_spaces: whitespace char matches any unicode whitespace char
        :param fffd_any: lets the \ufffd char match anything
        :param simplify: shorten the output regex via post-processing rules
        :param boundary: enforce boundary at edge of output regex using \b
        :return: regex string
        """
        assert list(self.tokenizer('test-test test')) == list('test-test test'), "shouldn't use a tokenizer"

        _parts = [[], []]
        _stack = [(self.head, sorted(self.head.keys(), reverse=True))]
        while _stack:
            head, keys = _stack.pop(-1)
            if keys:
                key = keys.pop(-1)
                _stack.append((head, keys))
                head = head[key]

                # add new item
                if _parts[-1]:
                    _parts[-1].append('|')

                # character escaping
                key = re.escape(key)

                # allow ascii quotes
                if fuzzy_quotes:
                    key = key.replace('\\\u2035', "[\\\u2035']")  # reversed prime
                    key = key.replace('\\\u2032', "[\\\u2032']")  # prime
                    key = key.replace('\\\u2018', "[\\\u2018']")  # left quote
                    key = key.replace('\\\u2019', "[\\\u2019']")  # right quote
                    key = key.replace('\\\u0060', "[\\\u0060']")  # grave
                    key = key.replace('\\\u00b4', "[\\\u00b4']")  # acute accent
                    key = key.replace('\\\u201d', '[\\\u201d"]')  # left double quote
                    key = key.replace('\\\u201c', '[\\\u201c"]')  # right double quote
                    key = key.replace('\\\u301d', '[\\\u301d"]')  # reversed double prime quotation mark
                    key = key.replace('\\\u301e', '[\\\u301e"]')  # double prime quotation mark

                # allow any whitesapce
                if fuzzy_spaces:
                    key = re.sub(r'\s', ' ', key)  # we'll do the \s replacement later

                # fffd matches any single character
                if fffd_any:
                    key = key.replace('\ufffd', '.')  # unicode replacement character

                _parts[-1].append(key)

                # one level down
                _stack.append((head, sorted(head.keys(), reverse=True)))
                _parts.append([])

            else:
                _current_parts = _parts.pop()
                if _current_parts:
                    if head.REPLACEMENT is not _SENTINEL:
                        _parts[-1].append('(?:')
                        _parts[-1].extend(_current_parts)
                        _parts[-1].append(')?')
                    elif len(head) != 1:
                        _parts[-1].append('(?:')
                        _parts[-1].extend(_current_parts)
                        _parts[-1].append(')')
                    else:
                        _parts[-1].extend(_current_parts)

        assert len(_parts) == 1
        _pattern = ''.join(_parts[0])

        if simplify:

            def char_group(match):
                out = ['[']
                sep = False
                escaped = False
                unicode = 0
                for char in match.groups()[0]:
                    if unicode:
                        assert not sep
                        out.append(char)
                        unicode -= 1
                        if not unicode:
                            sep = True

                    elif escaped:
                        assert not sep
                        out.append(char)
                        escaped = False
                        if char == '':
                            unicode = 4
                        elif char in '1234567890':
                            unicode = 2
                        else:
                            sep = True
                    elif char == '\\':
                        assert not sep
                        out.append('\\')
                        escaped = True
                    elif char == '|':
                        assert sep
                        sep = False
                    else:
                        assert not sep
                        out.append(char)
                        sep = True
                assert sep
                out.append(']')
                return ''.join(out)

            # this matches a single (possibly escaped) character
            _char = r'(?:\\(?:u\d\d\d\d|x\d\d|\d\d\d?|.)|[^\\])'

            # simplify `(?:x|y|z)` -> `[xyz]`
            _pattern = re.sub(r'(?<!\\)\(\?:({C}(?:\|{C})*)\)'.format(C=_char), char_group, _pattern)

            # simplify `(?:[xyz])` -> `[xyz]`
            _pattern = re.sub(r'(?<!\\)\(\?:(\[[^\[\]]*[^\[\]\\]\])\)', r'\1', _pattern)

            # simplify `(?:[xyz]?)?` -> `[xyz]?`
            _pattern = re.sub(r'(?<!\\)\(\?:(\[[^\[\]]*[^\[\]\\]\]\?)\)\??', r'\1', _pattern)

            # simplify `[.]` -> `.`
            _pattern = re.sub(r'(?<!\\)\[({C})\]'.format(C=_char), r'\1', _pattern)

            # simplify `(?:.)` -> `.`
            _pattern = re.sub(r'\(\?:({C})\)'.format(C=_char), r'\1', _pattern)

        # force surrounding brackets, and enforce word boundary
        if _pattern[3:] == '(?:':
            assert _pattern[-1] == ')'
            if boundary:
                _pattern = '(?:\\b%s\\b)' % _pattern[3:-1]
        elif boundary:
            _pattern = '(?:\\b%s\\b)' % _pattern
        else:
            _pattern = '(?:%s)' % _pattern

        if fuzzy_spaces:
            _pattern = _pattern.replace('\\ ', '\\s')
            assert ' ' not in _pattern

            while '\\s\\s' in _pattern:
                if '\\s\\s+' in _pattern:
                    _pattern = _pattern.replace('\\s\\s+', '\\s+')
                else:
                    _pattern = _pattern.replace('\\s\\s', '\\s+')
        else:
            _pattern = _pattern.replace('\\ ', ' ')

        # done
        return _pattern

    def keys(self):
        for key, value in self.items():
            yield key

    def values(self):
        for key, value in self.items():
            yield value

    def __delitem__(self, key):
        if type(key) is slice:
            for key, value in self._item_slice(key.start, key.stop, key.step):
                self.pop(key)
        else:
            self.pop(key)

    def update(self, replacements, verbose=True):
        """
        :type replacements: list[(str, str)] | dict[str, str] | Generator[(str, str), Any, None]
        :type verbose: bool
        """
        if type(replacements) is list:
            print_str = '(%%d pairs loaded out of %d)' % len(replacements)
        elif type(replacements) is dict:
            print_str = '(%%d pairs loaded out of %d)' % len(replacements)
            replacements = replacements.items()
        else:
            print_str = '(%d pairs loaded)'

        for index, (sequence, replacement) in enumerate(replacements):
            if verbose and (index + 1) % 50000 == 0:
                print(print_str % (index + 1))
            self[sequence] = replacement
        return self

    def _yield_tokens(self, file_path, encoding='utf8'):
        """
        yield tokens from a file given its path
        :param file_path: file to read
        """
        with io.open(file_path, mode=('rt', 'rb')[encoding is None], encoding=encoding) as _f:
            for token in self.tokenizer(char for line in _f for char in line):
                yield token

    def _translate(self, input_sequence):
        """
        processes text and yields output one token at a time
        :param input_sequence: iterable of hashable objects, preferably a string
        :type input_sequence: str | Iterable
        """
        output_buffer = collections.deque()  # [(index, token), ...]
        matches = dict()  # {span_start: (span_end + 1, REPLACEMENT), ...} <-- because: match == seq[start:end+1]
        spans = dict()  # positions that are partial matches: {span_start: span_head, ...}
        matches_to_remove = set()  # positions where matches may not start
        spans_to_remove = set()  # positions where matches may not start, or where matching failed

        for index, input_item in enumerate(input_sequence):
            # append new item to output_buffer
            output_buffer.append((index, input_item))

            # append new span to queue
            spans[index] = self.head

            # reset lists of things to remove
            matches_to_remove.clear()  # clearing is faster than creating a new set
            spans_to_remove.clear()

            # process spans in queue
            for span_start, span_head in spans.items():
                if input_item in span_head:
                    new_head = span_head[input_item]
                    spans[span_start] = new_head
                    if new_head.REPLACEMENT is not _SENTINEL:
                        matches[span_start] = (index + 1, new_head.REPLACEMENT)

                        # longest subsequence matching does not allow one match to start within another match
                        matches_to_remove.update(range(span_start + 1, index + 1))
                        spans_to_remove.update(range(span_start + 1, index + 1))

                else:
                    # failed to match the current token
                    spans_to_remove.add(span_start)

            # remove impossible spans and matches from queues
            for span_start in matches_to_remove:
                if span_start in matches:
                    del matches[span_start]
            for span_start in spans_to_remove:
                if span_start in spans:
                    del spans[span_start]

            # get indices of matches and spans
            first_match = min(matches) if matches else index
            first_span = min(spans) if spans else index

            # emit all matches that start before the first span
            while first_match < first_span:
                # take info
                match_end, match_replacement = matches[first_match]
                # emit until match start
                while output_buffer and output_buffer[0][0] < first_match:
                    yield output_buffer.popleft()[1]
                # clear output_buffer until match end
                while output_buffer and output_buffer[0][0] < match_end:  # remember match_end already has the +1
                    output_buffer.popleft()
                # emit replacement
                for item in match_replacement:
                    yield item
                # grab next match and retry
                del matches[first_match]
                first_match = min(matches) if matches else index

            # emit until span
            while output_buffer and output_buffer[0][0] < first_span:
                yield output_buffer.popleft()[1]

        # ignore remaining unmatched spans, yield matches only
        for match_start, (match_end, match_replacement) in sorted(matches.items()):
            # emit until match start
            while output_buffer and output_buffer[0][0] < match_start:  # remember match_end already has the +1
                yield output_buffer.popleft()[1]
            # clear output_buffer until match end
            while output_buffer and output_buffer[0][0] < match_end:  # remember match_end already has the +1
                output_buffer.popleft()
            # emit replacement one token at a time
            for token in self.tokenizer(match_replacement):
                yield token

        # emit remainder of output_buffer
        while output_buffer:
            yield output_buffer.popleft()[1]

    def find_all(self, input_sequence, allow_overlapping=False):
        """
        finds all occurrences within a string
        :param input_sequence: iterable of hashable objects
        :type input_sequence: str | Iterable
        :param allow_overlapping: yield all overlapping matches (soar -> so, soar, oar)
        :type allow_overlapping: bool
        """
        matches = dict()  # {span_start: (span_end + 1, [span_stuff, ...]), ...} <-- because: match == seq[start:end+1]
        spans = dict()  # positions that are partial matches: {span_start: (span_head, [span_stuff, ...]), ...}
        matches_to_remove = set()  # positions where matches may not start
        spans_to_remove = set()  # positions where matches may not start, or where matching failed

        for index, input_item in enumerate(self.tokenizer(input_sequence)):
            # append new span to queue
            spans[index] = (self.head, [])

            # reset lists of things to remove
            matches_to_remove.clear()  # clearing is faster than creating a new set
            spans_to_remove.clear()

            # process spans in queue
            for span_start, (span_head, span_seq) in spans.items():
                if input_item in span_head:
                    new_head = span_head[input_item]
                    span_seq.append(input_item)
                    spans[span_start] = (new_head, span_seq)
                    if new_head.REPLACEMENT is not _SENTINEL:
                        matches[span_start] = (index + 1, span_seq[:])

                        # longest subsequence matching does not allow one match to start within another match
                        if not allow_overlapping:
                            matches_to_remove.update(range(span_start + 1, index + 1))
                            spans_to_remove.update(range(span_start + 1, index + 1))

                else:
                    # failed to match the current token
                    spans_to_remove.add(span_start)

            # remove impossible spans and matches from queues
            for span_start in matches_to_remove:
                if span_start in matches:
                    del matches[span_start]
            for span_start in spans_to_remove:
                if span_start in spans:
                    del spans[span_start]

            # get indices of matches and spans
            first_span = min(spans) if spans else index
            while matches:
                match_start = min(matches)
                if match_start < first_span or allow_overlapping:
                    yield ''.join(matches[match_start][1])
                    del matches[match_start]
                else:
                    break

        for match_start, (match_end, matched_sequence) in sorted(matches.items()):
            yield ''.join(matched_sequence)

    def process_text(self, input_text):
        """

        :param input_text:
        :return:
        """
        return self.detokenizer(token for token in self._translate(self.tokenizer(input_text)))

    def process_file(self, input_path, output_path, overwrite=False, encoding='utf8'):
        """
        given a path:
        1. read the file
        2. replace all the things
        3. write the output to another file

        :type input_path: str
        :type output_path: str
        :type overwrite: bool
        :type encoding: str
        """

        if os.path.exists(output_path) and not overwrite:
            # skip and log to screen once per thousand files
            print('skipped: %s' % output_path)
        else:
            # recursively make necessary folders
            if not os.path.isdir(os.path.dirname(output_path)):
                assert not os.path.exists(os.path.dirname(output_path))
                os.makedirs(os.path.dirname(output_path))

            # process to temp file
            print('=' * 100)
            print('processing: %s' % input_path)
            print('input size: %s' % format_bytes(os.path.getsize(input_path)))
            temp_path = output_path + '.partial'
            t0 = time.time()

            try:
                with io.open(temp_path, mode=('wt', 'wb')[encoding is None], encoding=encoding) as _f:
                    for output_chunk in self._translate(self._yield_tokens(input_path, encoding=encoding)):
                        _f.write(output_chunk)

                print('    output: %s' % temp_path[:-8])

            except Exception:
                os.remove(temp_path)
                print('    failed: %s' % temp_path)
                raise

            # rename to output
            if os.path.exists(output_path):
                os.remove(output_path)
            os.rename(temp_path, output_path)
            t1 = time.time()
            print('total time: %s' % format_seconds(t1 - t0))


def self_test():
    # regex self-tests
    try:
        assert set(re.sub(r'\s', '', ''.join(UNICODE_SPACES), flags=re.U)) in [
            set('\u200b\u200c\u200d\u2060\u2800\ufeff'),
            set('\u180e\u200b\u200c\u200d\u2060\u2800\ufeff')]

    except AssertionError:
        print('whatever version of re you have has weird unicode spaces')
        print(repr(re.sub(r'\s', '', ''.join(UNICODE_SPACES), flags=re.U)))
        raise

    # feed in a list of tuples
    _trie = Trie()
    _trie.update([('asd', '111'), ('hjk', '222'), ('dfgh', '3333'), ('ghjkl;', '44444'), ('jkl', '!')])
    assert ''.join(_trie.process_text('erasdfghjkll')) == 'er111fg222ll'
    assert ''.join(_trie.process_text('erasdfghjkl;jkl;')) == 'er111f44444!;'
    assert ''.join(_trie.process_text('erassdfghjkl;jkl;')) == 'erass3333!;!;'
    assert ''.join(_trie.process_text('ersdfghjkll')) == 'ers3333!l'

    # fuzz-test regex
    # a-z
    permutations = []
    for a in 'abcde':
        for b in 'abcde':
            for c in 'abcde':
                for d in 'abcde':
                    permutations.append(a + b + c + d)

    # punctuation
    for a in '`~!@#$%^&*()-=_+[]{}\\|;\':",./<>?\0':
        for b in '`~!@#$%^&*()-=_+[]{}\\|;\':",./<>?\0':
            for c in '`~!@#$%^&*()-=_+[]{}\\|;\':",./<>?\0':
                permutations.append(a + b + c)

    # run fuzzer
    for _ in range(1000):
        chosen = set()
        for i in range(10):
            chosen.add(random.choice(permutations))
        _trie = Trie.fromkeys(chosen)
        r1 = re.compile(_trie.to_regex(fuzzy_quotes=False))  # fuzzy-matching quotes breaks this test
        for found in r1.findall(' '.join(permutations)):
            assert found in chosen
            chosen.remove(found)
        assert len(chosen) == 0

    # feed in a generator
    _trie = Trie()
    _trie.update(x.split('.') for x in 'a.b b.c c.d d.a'.split())
    assert ''.join(_trie.process_text('acbd')) == 'bdca'

    # feed in a dict
    _trie = Trie()
    _trie.update({
        'aa':                     '2',
        'aaa':                    '3',
        'aaaaaaaaaaaaaaaaaaaaaa': '~',
        'bbbb':                   '!',
    })

    assert 'aaaaaaa' not in _trie
    _trie['aaaaaaa'] = '7'

    assert ''.join(_trie.process_text('a' * 12 + 'b' + 'a' * 28)) == '732b~33'
    assert ''.join(_trie.process_text('a' * 40)) == '~773a'
    assert ''.join(_trie.process_text('a' * 45)) == '~~a'
    assert ''.join(_trie.process_text('a' * 25)) == '~3'
    assert ''.join(_trie.process_text('a' * 60)) == '~~772'

    del _trie['bbbb']
    assert 'b' not in _trie.head

    del _trie['aaaaaaa']
    assert 'aaa' in _trie
    assert 'aaaaaaa' not in _trie
    assert 'aaaaaaaaaaaaaaaaaaaaaa' in _trie

    _trie['aaaa'] = 4

    del _trie['aaaaaaaaaaaaaaaaaaaaaa']
    assert 'aaa' in _trie
    assert 'aaaaaaa' not in _trie
    assert 'aaaaaaaaaaaaaaaaaaaaaa' not in _trie

    assert len(_trie.head['a']['a']['a']) == 1
    assert len(_trie.head['a']['a']['a']['a']) == 0

    del _trie['aaa':'bbb']
    assert _trie.to_regex() == '(?:aa)'

    # fromkeys
    _trie = Trie.fromkeys('mad gas scar madagascar scare care car career error err are'.split())

    test = 'madagascareerror'
    assert list(_trie.find_all(test)) == ['madagascar', 'error']
    assert list(_trie.find_all(test, True)) == ['mad', 'gas', 'madagascar',
                                                'scar', 'car', 'scare', 'care',
                                                'are', 'career', 'err', 'error']

    _trie = Trie.fromkeys('to toga get her here there gather together hear the he ear'.split())

    test = 'togethere'
    assert list(_trie.find_all(test)) == ['together']
    assert list(_trie.find_all(test, True)) == ['to', 'get', 'the', 'he',
                                                'together', 'her', 'there', 'here']

    test = 'togethear'
    assert list(_trie.find_all(test)) == ['to', 'get', 'hear']
    assert list(_trie.find_all(test, True)) == ['to', 'get', 'the', 'he', 'hear', 'ear']

    # test special characters
    _trie = Trie.fromkeys('| \\ \\| |\\ [ () (][) ||| *** *.* **| \\\'\\\' (?:?) \0'.split())
    assert re.findall(_trie.to_regex(), '***|\\||||') == ['***', '|\\', '|||', '|']


if __name__ == '__main__':
    self_test()

    # define input/output
    input_folder = os.path.abspath('test/input')
    output_folder = os.path.abspath('test/output')
    file_name_pattern = '*'

    # you can use a generator for the mapping to save memory space
    mapping = [(line.split()[0], line.split()[-1][::-1]) for line in yield_lines('test/input/english-long.txt')]
    print('%d pairs of replacements' % len(mapping))

    # parse mapping list into trie with a tokenizer
    print('parse map to trie...')
    t_init = datetime.datetime.now()
    # m_init = psutil.virtual_memory().used

    # set tokenizer
    trie = Trie(lexer=space_tokenize)
    trie.update(mapping, verbose=True)
    # m_end = psutil.virtual_memory().used
    t_end = datetime.datetime.now()
    print('parse completed!', format_seconds((t_end - t_init).total_seconds()))
    # print('memory usage:', format_bytes(m_end - m_init))

    # start timer
    t_init = datetime.datetime.now()
    print('processing start...', t_init)

    # process everything using the same tokenizer
    for path in glob.iglob(os.path.join(input_folder, '**', file_name_pattern), recursive=True):
        if os.path.isfile(path):
            new_path = path.replace(input_folder, output_folder)
            trie.process_file(path, new_path, overwrite=True)

    # stop timer
    t_end = datetime.datetime.now()
    print('')
    print('processing complete!', t_end)
    print('processing total time:', format_seconds((t_end - t_init).total_seconds()))
    print('processing total time:', (t_end - t_init))

    # just find all matches, don't replace
    t = time.time()
    with open('test/input/kjv.txt') as f:
        content = f.read()
    for _ in trie.find_all(content):
        pass
    print('find_all took this long:', format_seconds(time.time() - t))

    # no tokenizer is better if you want to build a regex
    # no tokenizer matches and replaces any substring, not just words
    trie2 = Trie()
    trie2.update(mapping[:1000], verbose=True)

    # create regex
    print(trie2.to_regex(boundary=True))
    print(len(trie2.to_regex(boundary=True)))

    # short code to make regex
    print(Trie.fromkeys(['bob', 'bobo', 'boba', 'baba', 'bobi']).to_regex())
    print(Trie.fromkeys(['bob', 'bobo', 'boba', 'baba', 'bobi']).to_regex(simplify=False))
    print(Trie.fromkeys(['pen', 'pineapple', 'apple', 'pencil']).to_regex())
    print(Trie.fromkeys(['pen', 'pineapple', 'apple', 'pencil']).to_regex(boundary=True))

    # test space in regex
    print(repr(Trie.fromkeys(['bo b', 'bo bo', 'boba', 'ba  ba', 'bo bi']).to_regex()))
