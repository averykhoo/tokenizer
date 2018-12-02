# aho-corasick-string-replacement
replace multiple strings with multiple other strings in a single pass


## todo
- make readme
- neaten code
- convert trie to DFA
- parallel work sharing to make processing faster
- add options to the to_regex function (`space` -> `\s`, etc)
- simplify `(?:x|y|z)` -> `[xyz]`
- find_all case insensitive
- find_all find first only or None, na=False
- None or na -> use empty string as replacement
- specify case=False in init
- case insensitivity in the tokenizer instead?
- add code history from 2016
- split out the tokenizer maybe
- lowercase in the tokenizer? or in the trie?