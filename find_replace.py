"""
given a large bunch (~1e7) of things to find and replace and a folder of data to clean
and writes the cleaned copied data to the output folder, preserving the relative path

if a tokenizer is used, only matches at token boundaries
"""
import collections
import datetime
import glob
import io
import math
import os
import random
import re
import time

import psutil

try:
    from tokenizer import _is_punctuation_char, _is_space_char

except ImportError:
    def _is_punctuation_char(char):
        return char in {
            # COMMON PUNCTUATION
            '!', '"', '#', '$', '%', '&', "'", '(', ')', '*', '+', ',', '-', '.', '/', ':', ';', '<', '=', '>', '?',
            '@', '[', '\\', ']', '^', '_', '`', '{', '|', '}', '~', '‘', '’', '“', '”', '§', '±', '√', '\u2014',
            '\u2013', '\u2025', '\u2026', '\u22ee', '\u3002', '\u300e', '\u300f', '\u300c', '\u300d', '\ufe41',
            '\ufe42', '\u3001', '\u2022', '\u2027', '\u300a', '\u300b', '\u3008', '\u3009', '\ufe4f', '\uff0c',
            '\uff01', '\uff1f', '\uff1b', '\uff1a', '\uff08', '\uff09', '\uff3b', '\uff3d', '\u3010', '\u3011',
            # UNPRINTABLE CHARS
            '\u0000', '\u0001', '\u0002', '\u0003', '\u0004', '\u0005', '\u0006', '\u0007', '\u0008', '\u000e',
            '\u000f', '\u0010', '\u0011', '\u0012', '\u0013', '\u0014', '\u0015', '\u0016', '\u0017', '\u0018',
            '\u0019', '\u001a', '\u001b', '\u007f', '\uffef', '\ufffd'}


    def _is_space_char(char):
        return char in {'\t', '\n', '\v', '\f', '\r', ' ', '\x85', '\xa0', '\x1c', '\x1d', '\x1e', '\x1f', '\ufeff',
                        '\u1680', '\u2000', '\u2001', '\u2002', '\u2003', '\u2004', '\u2005', '\u2006', '\u2007',
                        '\u2008', '\u2009', '\u200a', '\u2028', '\u2029', '\u202f', '\u205f', '\u3000', '\u180e',
                        '\u200b', '\u200c', '\u200d', '\u2060', '\u2800'}  # UNICODE SPACES


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


def space_tokenize(text, token_max_len=65535, emit_space=True, emit_punctuation=True):
    """
    tokenize by whitespace and punctuation

    :param text: to be split
    :param token_max_len: truncate tokens after this length
    :param emit_space: emit spaces
    :param emit_punctuation: emit punctuation
    """
    # init
    space_char = ''
    text_buffer = []

    # main loop over all text
    for char in text:
        # 1) spaces
        if _is_space_char(char):
            if char == space_char and len(text_buffer) < token_max_len:
                text_buffer.append(char)
            else:
                if text_buffer:
                    yield ''.join(text_buffer)
                if emit_space:
                    space_char = char
                    text_buffer = [char]
                else:
                    space_char = ''

        # 2) punctuation
        elif _is_punctuation_char(char):
            if text_buffer:
                yield ''.join(text_buffer)
            if emit_punctuation:
                yield char
            space_char = ''
            text_buffer = []

        # 3) first char
        elif space_char:
            if text_buffer:
                yield ''.join(text_buffer)
            space_char = ''
            text_buffer = [char]

        # 4) next char
        elif len(text_buffer) < token_max_len:
            text_buffer.append(char)

        # 5) max char
        else:
            yield ''.join(text_buffer)
            text_buffer = [char]

    # finally, yield the last chunk
    if text_buffer:
        yield ''.join(text_buffer)


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

    def __init__(self, replacements=None, tokenizer=None, detokenizer=None, case_sensitive=False):
        """

        :param replacements:
        :param tokenizer: tokenizer that reads one character at a time and yields tokens
        :type tokenizer: Iterable -> Iterable
        :param detokenizer: function to combine tokens back into a string
        :param case_sensitive: if False, lowercase all the things (including output)
        """
        self.head = self.Node()

        if tokenizer is None:
            if case_sensitive:
                def _list_tokenizer(seq):
                    for elem in seq:
                        yield elem

                self.tokenizer = _list_tokenizer
            else:
                def _lowercase_list_tokenizer(seq):
                    for elem in seq:
                        yield elem.lower()

                self.tokenizer = _lowercase_list_tokenizer
        elif case_sensitive:
            def _lowercase_wrap_tokenizer(seq):
                for elem in tokenizer(seq):
                    yield elem.lower()

            self.tokenizer = _lowercase_wrap_tokenizer
        else:
            self.tokenizer = tokenizer

        if detokenizer is None:
            def _list_detokenizer(seq):
                return ''.join(seq)

            self.detokenizer = _list_detokenizer
        else:
            self.detokenizer = detokenizer

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
        # empty Trie, so behave like an empty set
        if not self.head.keys():
            raise KeyError(key)

        # pop first item if key not specified
        if key is None:
            for key in self.keys():
                break

        head = self.head
        breadcrumbs = [(None, head)]
        for token in self.tokenizer(key):
            head = head.setdefault(token, self.Node())
            breadcrumbs.append((token, head))
        if head.REPLACEMENT is _SENTINEL:
            raise KeyError(key)
        replacement = head.REPLACEMENT
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
        return key, replacement

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


def to_regex(list_of_strings,
             case_sensitive=False,
             fuzzy_quotes=True,
             fuzzy_spaces=True,
             fffd_any=True,
             simplify=True,
             boundary=False):
    _trie = Trie.fromkeys(list_of_strings, case_sensitive=case_sensitive)
    return _trie.to_regex(fuzzy_quotes=fuzzy_quotes,
                          fuzzy_spaces=fuzzy_spaces,
                          fffd_any=fffd_any,
                          simplify=simplify,
                          boundary=boundary)


def self_test():
    # regex self-tests
    _spaces = '\t\n\v\f\r \x85\xa0\x1c\x1d\x1e\x1f\ufeff\u1680\u2000\u2001\u2002\u2003\u2004\u2005\u2006' \
              '\u2007\u2008\u2009\u200a\u2028\u2029\u202f\u205f\u3000\u180e\u200b\u200c\u200d\u2060\u2800'
    try:
        assert set(re.sub(r'\s', '', _spaces, flags=re.U)) in [
            set('\u200b\u200c\u200d\u2060\u2800\ufeff'),
            set('\u180e\u200b\u200c\u200d\u2060\u2800\ufeff')]

    except AssertionError:
        print('whatever version of re you have has weird unicode spaces', repr(re.sub(r'\s', '', _spaces, flags=re.U)))
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
    _trie.update({'a': 'b', 'b': 'c', 'c': 'd', 'd': 'a'})
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
    m_init = psutil.virtual_memory().used

    # set tokenizer
    trie = Trie(tokenizer=space_tokenize)
    trie.update(mapping, verbose=True)
    m_end = psutil.virtual_memory().used
    t_end = datetime.datetime.now()
    print('parse completed!', format_seconds((t_end - t_init).total_seconds()))
    print('memory usage:', format_bytes(m_end - m_init))

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
    print(to_regex(['bob', 'bobo', 'boba', 'baba', 'bobi']))
    print(to_regex(['bob', 'bobo', 'boba', 'baba', 'bobi'], simplify=False))
    print(to_regex(['pen', 'pineapple', 'apple', 'pencil']))
    print(to_regex(['pen', 'pineapple', 'apple', 'pencil'], boundary=True))

    # test space in regex
    print(repr(to_regex(['bo b', 'bo bo', 'boba', 'ba  ba', 'bo bi'])))
