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
d1_index = bow.add_document('the quick brown fox jumped over'.split())

# add document 2 (with a doc_id)
d2_index = bow.add_document('the lazy dog'.split(), document_id='d2')

# calculate idf
# note: you can mix and duplicate doc_ids and indices
idf = bow.idf([d1_index, 'd2', 'd2'])

# set doc_id, or duplicate a bow from its doc_id
bow.set_document_id('d1', d1_index)

# duplicate a bow to a new doc_id
bow.set_document_id('d3', d1_index)

# re-calculate idf with new doc_ids
idf2 = bow.idf(['d1', 'd2', 'd2', 'd3'])
```

### Other things
-   `bow.vocabulary` : list of all seen words
-   `bow.words(<doc_ids>)` : merged bag of words across all specified docs
-   `bow.word_counts(<doc_ids>)` : merged wordcount across all specified docs
-   `bow.unique_words(<doc_ids>)` : set of words that appear in specified docs
-   `bow.num_unique_words(<doc_ids>)` : number of words in `unique_words`
-   `bow.stopwords(<doc_ids>, <stopword_df>)` : find stopwords by how frequently they occur
    -   `stopword_df` is the fraction of documents a word has to appear in to become a stopword
