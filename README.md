#   Aho-Corasick Find & Replace
-   Given a dict from strings to other strings, replaces all occurrences non-recursively
-   Fast because it does a single pass over the target string
-   (Incompletely) based on [Aho-Corasick string search](https://en.wikipedia.org/wiki/Aho–Corasick_algorithm), 
    but modified to perform replacements
    -   Uses a [trie](https://en.wikipedia.org/wiki/Trie) structure *without* suffix links, 
        so that you can dynamically add/remove stuff
-   If you only want to search, use another library (e.g. [`pyahocorasick`](https://pypi.org/project/pyahocorasick/) or [`python-hyperscan`](https://pypi.org/project/hyperscan/))


##  TL;DR

### Convert list of strings into a regex:
-   Single line: `print(to_regex(['pen', 'pineapple', 'apple', 'pencil']))`
```python
from find_replace import to_regex

strings = ['pen', 'pineapple', 'apple', 'pencil']

pattern = to_regex(strings, lowercase=True)
print(pattern)  # '(?:(?:apple|p(?:en(?:cil)?|ineapple)))'
```
-   Why is space being changed to match all whitespace ('\s')?
    -   Fuzzy spaces make life easier
    -   To disable, use `to_regex(fuzzy_spaces=False)`
-   Why is the black shape ('\uFFFD') being changed to match any ('.')?
    -   '\uFFFD' is a char that could have been anything
    -   To disable, use `to_regex(fffd_any=False)`
-   What's happening to my curly quotes?
    -   To disable, use `to_regex(fuzzy_quotes=False)`

### Find occurrences of a list of strings
```python
from find_replace import Trie

target = 'I have a pen... I have an apple...'
strings = ['pen', 'pineapple', 'apple', 'pencil']

trie = Trie.fromkeys(strings)
matches = trie.findall(target)  # `findall` returns a list of str
print(matches)  # ['pen', 'apple']
```
-   How do I do incremental search (via a generator)?
    -   `trie.finditer(target)`
-   How do I make it case insensitive?
    -   Use `trie = Trie.fromkeys(strings, lowercase=True)`
    -   *You must a case-insensitive trie to perform case-insensitive search, and vice versa* 
-   How do I find overlapping matches?
    -   Use `trie.findall(target, allow_overlapping=True)`
    -   Or `trie.finditer(target, allow_overlapping=True)`
    -   *Note that you cannot perform replacements on overlapping matches*
-   How do I get Match objects (like the builtin `re.finditer`)?
    -   `trie.finditer(target)`
    -   *Note that not all properties of the re.Match object are available* 

### Replace occurrences of some strings with other strings
```python
from find_replace import Trie

target = 'I have a pen... I have an apple...'
replacements = {'pen': 'pineapple', 'apple': 'pencil'}

trie = Trie(replacements)
output = trie.translate(target)
print(output)  # 'I have a pineapple... I have an pencil...'
```
-   How do I make it case insensitive?
    -   Not implemented
-   Why is it finding substrings (e.g. "java" in "javascript")?
    -   That's just what a string search should do...
    -   To match at word boundaries, specify a tokenizer when creating the trie
        -   First: `from tokenizer import unicode_tokenize` <-- tokenizes on spaces and punctuation
        -   Then: `trie = Trie(replacements, lexer=unicode_tokenize)`

### Replace occurrences of some strings with a specific string
```python
from find_replace import Trie

target = 'I have a pen... I have an apple...'
strings = ['pen', 'pineapple', 'apple', 'pencil']

trie = Trie.fromkeys(strings, 'orange')
output = trie.translate(target)
print(output)  # 'I have a orange... I have an orange...'
```
-   How do I remove instead of replace?
    -   Use `Trie.fromkeys(strings, '')`

##  Advanced Usage

| Function       | Explanation                                   | Usage                                                   |
|:---------------|:----------------------------------------------|:--------------------------------------------------------|
| `update`       | add/modify replacements                       | `trie.update({'apple', 'orange', 'orange': 'apple'})`   |
| `__setitem__`  | add/modify replacements                       | `trie['pen apple'] = 'apple pen'`                       |
| `__getitem__`  | see what you've inserted                      | `print(trie['pen'])` or `print(trie['apple':'orange'])` |
| `process_file` | replace stuff in some text file to a new file | `trie.process_file(input_path, output_path)`            |
| `__delitem__`  | remove a string-replacement pair              | `del trie['pen']`                                       |


##  To-Do
-   refactor code into multiple files?
-   parallelize file processing to make processing faster, sharing a single trie

-   find a way to convert trie to DFA by computing suffix/failure links
    -   while still allowing in-place updates to the trie
    -   checked the literature, doesn't seem possible to implement in a simple way
    -   requires inverted failure link map

-   check why flashtext algo is faster
    -   because it does't handle unicode? (unlikely)
    -   because the simpler algo has fewer branches? (likely)
        -   with bugs (if input ends with space)
        -   loads everything into memory to work with, assumes no IO bound
        -   has an illegal word "_keyword_" to simplify the algo
    -   doesn't support find all overlapping
    - 
    -   because it favors average case (short matches) and ignores the psychopathic worst case? (true but not too bad)

-   fix case insensitive replacement
-   maybe mimic flashtext for average case
    -   welp lesson learned here, better big O may not mean better overall performance
    -   modified to use generators
    -   and a decent tokenizer

-   run tokenizer on file `tokenize(open('test.txt'))`
-   min (key)
-   max (key)
-   predecessor (key)
-   successor (key)
-   match should be in string indices, not token indices
-   findall case insensitive should return case sensitive matches
-   test len in the following cases:
    -   delete
    -   setdefault
    -   set
    -   update many (including existing)
    -   set existing
-   slice on integer indices
-   index of string (e.g. `['a', 'b', 'c'].index('b')`)
-   support for word boundaries without tokenizer?
    -   but this would slow down the algo since we might be checking for boundaries twice

##  Notes on Aho Corasick string search
-   to implement incremental AC, we need an inverse failure link tree
-   we can't implement failure links on a DAWG
-   if failure links are implemented just right, we can probably get a DFA
-   failure link and match implementation depend on how we want to return results
    -   return all?
    -   return first longest?
-   recursive failure generation:
    -   `node.next[char].fail = node.fail.next[char] or root_node.next[char]`
    -   or `node.fail = node.parent.fail[char]`
    -   can be done dfs or bfs, no difference
-   can't actually use dataclass because not compatible with slots
