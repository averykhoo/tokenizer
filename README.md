# aho-corasick-string-replacement
replace multiple strings with multiple other strings in a single pass
uses the aho-corasick string search algorithm, but only considers the first longest match

## usage
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

