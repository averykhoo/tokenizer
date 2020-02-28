#   tokenizer
```python
from tokenizer import unicode_tokenize
from tokenizer import word_n_grams
from tokenizer import sentence_split
from tokenizer import sentence_split_tokens

# to get strings from a generator
unicode_tokenize('the quick brown fox. the lazy dog.')  # includes spaces & punctuation
unicode_tokenize('the quick brown fox. the lazy dog.', words_only=True)

# to get word n-grams
word_n_grams('the quick brown fox. the lazy dog.', n=2)  # splits into sentences first so that n-grams don't span multiple sentences

# to get Token objects
unicode_tokenize('the quick brown fox. the lazy dog.', as_tokens=True)  # includes spaces & punctuation
unicode_tokenize('the quick brown fox. the lazy dog.', words_only=True, as_tokens=True)

# to split sentences
sentence_split('the quick brown fox. the lazy dog.')  # yields each sentence as a str
sentence_split_tokens('the quick brown fox. the lazy dog.')  # yields each sentence as a list of Token objects
```


#   Git submodules
##  Add
-   `git submodule add https://github.com/averykhoo/tokenizer.git`
-   `git add tokenizer`  (is this needed?)
##  Update
-   `git submodule update --init --recursive --remote --force`
