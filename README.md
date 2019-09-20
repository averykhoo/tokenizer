#   Aho-Corasick Find & Replace
-   Given a dict from strings to other strings, replaces all occurrences non-recursively
-   Fast because it does a single pass over the target string
-   (Incompletely) based on [Aho-Corasick string search](https://en.wikipedia.org/wiki/Aho–Corasick_algorithm), 
    but modified to perform replacements
    -   Uses a [trie](https://en.wikipedia.org/wiki/Trie) structure *without* suffix links, 
        so that you can dynamically add/remove stuff


##  TL;DR

### Convert list of strings into a regex:
```python
from find_replace import Trie

strings = ['pen', 'pineapple', 'apple', 'pencil']

trie = Trie.fromkeys(strings, case_sensitive=False)
pattern = trie.to_regex()
print(pattern)  # '(?:(?:apple|p(?:en(?:cil)?|ineapple)))'
```
-   Single line: `print(Trie.fromkeys(['pen', 'pineapple', 'apple', 'pencil'], case_sensitive=False).to_regex())`
-   Why is space being changed to match all whitespace ('\s')?
    -   Fuzzy spaces make life easier
    -   To disable, use `trie.to_regex(fuzzy_spaces=False)`
-   Why is the black shape ('\uFFFD') being changed to match any ('.')?
    -   '\uFFFD' is a char that could have been anything
    -   To disable, use `trie.to_regex(fffd_any=False)`
-   What's happening to my curly quotes?
    -   To disable, use `trie.to_regex(fuzzy_quotes=False)`

### Find occurrences of a list of strings
```python
from find_replace import Trie

target = 'I have a pen... I have an apple...'
strings = ['pen', 'pineapple', 'apple', 'pencil']

trie = Trie.fromkeys(strings)
matches = list(trie.find_all(target))  # `find_all` returns a generator
print(matches)  # ['pen', 'apple']
```
-   How do I make it case insensitive?
    -   Use `trie = Trie.fromkeys(strings, case_sensitive=False)`
-   How do I find overlapping matches?
    -   Use `trie.find_all(target, allow_overlapping=True)`

### Replace occurrences of some strings with other strings
```python
from find_replace import Trie

target = 'I have a pen... I have an apple...'
replacements = {'pen': 'pineapple', 'apple': 'pencil'}

trie = Trie(replacements)
output = trie.process_text(target)
print(output)  # 'I have a pineapple... I have an pencil...'
```
-   How do I make it case insensitive?
    -   Use `trie = Trie(replacements, case_sensitive=False)`

### Replace occurrences of some strings with a specific string
```python
from find_replace import Trie

target = 'I have a pen... I have an apple...'
strings = ['pen', 'pineapple', 'apple', 'pencil']

trie = Trie.fromkeys(strings, 'orange')
output = trie.process_text(target)
print(output)  # 'I have a orange... I have an orange...'
```
-   How do I remove instead of replace?
    -   Use `Trie.fromkeys(strings, '')`

##  Advanced Usage

-   `update` <--
-   `__setitem__` <--
-   get (with slices)
-   `process_file` <-- replace stuff in a text file
-   `__delitem__` <-- 

##  To-Do
-   finish readme
-   refactor code into multiple files
-   convert trie to DFA by computing suffix/failure links
-   parallel file processing to make processing faster, sharing a single trie
-   split into find-only and find + replace
-   unicode tokenize like fts5
-   find a way to add suffix links while allowing in-place updates to the trie

