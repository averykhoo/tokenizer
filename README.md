#   aho-corasick-string-replacement
replace multiple strings with multiple other strings in a single pass
uses the aho-corasick string search algorithm, but only considers the first longest match

##  usage

-   `fromkeys` <--
-   `update` <--
-   `__setitem__` <--
-   get (with slices)
-   `process_text` <-- replace stuff in a string
-   `process_file` <-- replace stuff in a text file
-   `find_all` <-- find stuff in a string
-   `to_regex` <-- convert the entire trie into a regex
-   `__delitem__` <-- 

##  todo
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

