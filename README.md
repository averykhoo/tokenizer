# aho-corasick-string-replacement
replace multiple strings with multiple other strings in a single pass
uses the aho-corasick string search algorithm, but only considers the first longest match

## usage
-   `fromkeys` <--
-   `update`
-   `__setitem__`
-   `process_text` <-- replace stuff in a string
-   `process_file` <-- replace stuff in a text file
-   `find_all` <-- find stuff in a string
-   `to_regex` <-- convert the entire trie into a regex

## todo
- make readme
- neaten and refactor code into multiple files
- convert trie to DFA by computing suffix/failure links
- parallel work sharing to make processing faster
- add code history from 2016
- split out the tokenizer maybe
- cleanup and deconflict interfaces
  - list-style interface (with slices)
  - set-style interface (add, remove)
  - dict-style interface (like a set, but with keys)
  - iterator-style interface
  - regex interface (improve regex optimization, more like re.findall/match/etc)
- `__del__`
- disable `fromkeys()` once created

