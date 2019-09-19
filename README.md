#   Aho-Corasick Find & Replace
-   replace multiple strings with multiple other strings in a single pass
-   uses the aho-corasick string search algorithm, but only considers the first longest match


##  TL;DR

### Convert list of strings into a regex:
```python
from find_replace import AhoCorasickReplace

strings = ['pen', 'pineapple', 'apple', 'pencil']

trie = AhoCorasickReplace.fromkeys(strings, case_sensitive=False)
pattern = trie.to_regex()
print(pattern)  # '(?:(?:apple|p(?:en(?:cil)?|ineapple)))'
```
-   Single line: `print(AhoCorasickReplace.fromkeys(['pen', 'pineapple', 'apple', 'pencil'], case_sensitive=False).to_regex())`
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
from find_replace import AhoCorasickReplace

target = 'I have a pen... I have an apple...'
strings = ['pen', 'pineapple', 'apple', 'pencil']

trie = AhoCorasickReplace.fromkeys(strings)
matches = list(trie.find_all(target))  # `find_all` returns a generator
print(matches)  # ['pen', 'apple']
```
-   How do I make it case insensitive?
    -   Use `trie = AhoCorasickReplace.fromkeys(strings, case_sensitive=False)`

### Replace occurrences of some strings with other strings
```python
from find_replace import AhoCorasickReplace

target = 'I have a pen... I have an apple...'
replacements = {'pen': 'pineapple', 'apple': 'pencil'}

trie = AhoCorasickReplace(replacements)
output = trie.process_text(target)
print(output)  # 'I have a pineapple... I have an pencil...'
```
-   How do I make it case insensitive?
    -   Use `trie = AhoCorasickReplace(replacements, case_sensitive=False)`

### Replace occurrences of some strings with a specific string
```python
from find_replace import AhoCorasickReplace

target = 'I have a pen... I have an apple...'
strings = ['pen', 'pineapple', 'apple', 'pencil']

trie = AhoCorasickReplace.fromkeys(strings, 'orange')
output = trie.process_text(target)
print(output)  # 'I have a orange... I have an orange...'
```
-   How do I remove instead of replace?
    -   Use `AhoCorasickReplace.fromkeys(strings, '')`

##  Advanced Usage

-   `fromkeys` <--
-   `update` <--
-   `__setitem__` <--
-   get (with slices)
-   `process_text` <-- replace stuff in a string
-   `process_file` <-- replace stuff in a text file
-   `find_all` <-- find stuff in a string
-   `to_regex` <-- convert the entire trie into a regex
-   `__delitem__` <-- 

##  To-Do
-   make readme
-   neaten and refactor code into multiple files
-   convert trie to DFA by computing suffix/failure links
-   parallel work sharing to make processing faster
-   split out the tokenizer maybe
-   cleanup and deconflict interfaces
    -   set-style interface (add, remove)
    -   iterator-style interface
-   disable `fromkeys()` once created
-   unicode tokenize like fts5

