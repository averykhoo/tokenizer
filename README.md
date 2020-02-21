#   Bag of words Corpus
-   given bags of words, store them in an index
-   index is as small as possible, uses a vocabulary for 'compression'


##  Usage
### TLDR version
```python
from bag_of_words import BagOfWordsCorpus

# create object
bow = BagOfWordsCorpus()

# add document 1
d1_index = bow.add_document('the quick brown fox jumped over the lazy dog'.split())

# add document 2 (with a document id)
bow.add_document('the quick brown fox jumped over the lazy dog'.split(), document_id='d2')

# calculate idf
idf = bow.idf([d1_index, 'd2', 'd2'])  # you can mix and duplicate ids and indices
```

### Other things
-   `bow.vocabulary` : list of all seen words
-   `bow.words(<doc_ids>)` : merged bag of words across all specified docs
-   `bow.word_counts(<doc_ids>)` : merged wordcount across all specified docs
-   `bow.unique_words(<doc_ids>)` : set of words that appear in specified docs
-   `bow.num_unique_words(<doc_ids>)` : number of words in `unique_words`
-   `bow.stopwords(<doc_ids>, <stopword_df>)` : find stopwords by how frequently they occur
    -   `stopword_df` is the fraction of documents a word has to appear in to become a stopword
