import os
import time

from find_replace import Trie
from tokenizer import unicode_tokenize


def yield_lines(file_path, make_lower=False, threshold_len=0):
    """
    yields all non-empty lines in a file

    :param file_path: file to read
    :param make_lower: force line to lowercase
    :param threshold_len: ignore lines equal <= this length
    """
    with open(file_path, mode='rt', encoding='utf-8') as _f:
        for line in _f:
            line = line.strip()
            if make_lower:
                line = line.lower()
            if len(line) > threshold_len:
                yield line


def process_file(kwp, input_path, output_path, overwrite=False, encoding='utf8'):
    """
    given a path:
    1. read the file
    2. replace all the things
    3. write the output to another file

    :type input_path: str
    :type output_path: str
    :type overwrite: bool
    :type encoding: str | None
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
        print('input size: %s' % os.path.getsize(input_path))
        temp_path = output_path + '.partial'
        t0 = time.time()

        try:
            with open(temp_path, mode=('wt', 'wb')[encoding is None], encoding=encoding) as _f:
                for line in yield_lines(input_path):
                    _f.write(kwp.translate(line))
                    _f.write('\n')

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
        print('total time: %s' % (t1 - t0))


keyword_processor = Trie(lowercase=True, tokenizer=unicode_tokenize)
for line in yield_lines('test/input/english-long.txt'):
    keyword_processor[line.split()[0]] = line.split()[-1][::-1]

# print('%d pairs of replacements' % len(keyword_processor))

new_sentence = keyword_processor.translate('I love Big Apple and new delhi.')
print(new_sentence)

# process_file(keyword_processor, 'test/input/kjv.txt', 'tmp/kjv2.txt', overwrite=True)

keyword_processor['a ' * 1000 + 'b'] = 'b'
# keyword_processor[('a ' * 100 ).strip()+'c'] ='c'
keyword_processor['a'] = 'd'
text = 'a ' * 100000 + 'b c'

t = time.time()
tmp = keyword_processor.translate(text)
print(time.time() - t)
print(len(tmp))
