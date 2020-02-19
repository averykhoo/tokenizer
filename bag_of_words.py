import math
import pickle
import warnings
from collections import Counter
from dataclasses import dataclass
from dataclasses import field
from typing import Any
from typing import Dict
from typing import Generator
from typing import Iterable
from typing import List
from typing import Set
from typing import Tuple


@dataclass
class BagOfWordsCorpus:
    # actual documents bags-of-words stored here, as tuples of (word_idx, word_count), sorted by word_count descending
    corpus: List[Tuple[Tuple[int, int], ...]] = field(default_factory=list)

    # vocabulary: word <-> word_index
    _vocabulary_to_idx: Dict[str, int] = field(default_factory=dict)
    _vocabulary: List[str] = field(default_factory=list)

    def word_to_index(self, word: str) -> int:
        # not thread safe!

        # known word
        if word in self._vocabulary_to_idx:
            return self._vocabulary_to_idx[word]

        # add word
        assert isinstance(word, str), word
        _idx = self._vocabulary_to_idx[word] = len(self._vocabulary)
        self._vocabulary.append(word)

        # double-check invariants before returning
        assert len(self._vocabulary_to_idx) == len(self._vocabulary) == _idx + 1
        assert self._vocabulary[_idx] == word, (self._vocabulary[_idx], word)  # check race condition
        return _idx

    def index_to_word(self, word_index: int) -> str:
        return self._vocabulary[word_index]

    def add_document(self, document_words: Iterable[str]) -> int:
        # not thread safe!
        c = Counter(self.word_to_index(word) for word in document_words)
        self.corpus.append(tuple(c.most_common()))
        return len(self.corpus) - 1  # this is the document index

    def word_counts(self, document_index: int, normalize: bool = False) -> Dict[str, int]:
        if normalize:
            total_words = self.num_words(document_index)
            return {self._vocabulary[word_idx]: count / total_words for word_idx, count in self.corpus[document_index]}
        else:
            return {self._vocabulary[word_idx]: count for word_idx, count in self.corpus[document_index]}

    def idf(self, document_indices: Iterable[int], add_one_smoothing: bool = True) -> Dict[str, float]:

        # count words
        _idx_idf = Counter()
        n_docs = 0
        for document_idx in document_indices:
            n_docs += 1
            _idx_idf.update(word_idx for word_idx, _ in self.corpus[document_idx])

        # smoothing for idf
        add_smooth = 1 if add_one_smoothing else 0
        n_docs += add_smooth

        # log + 1 helps avoid idf == 0 for words that exist in all docs
        return {self._vocabulary[word_idx]: math.log(n_docs / (count + add_smooth)) + 1
                for word_idx, count in _idx_idf.most_common()}

    def stopwords(self, document_indices: Iterable[int], stopword_df=0.85) -> Set[str]:
        assert 0.0 < stopword_df <= 1.0

        # no stopwords if no limit
        if stopword_df == 1.0:
            return set()

        # count words
        _idx_idf = Counter()
        n_docs = 0
        for document_idx in document_indices:
            n_docs += 1
            _idx_idf.update(word_idx for word_idx, _ in self.corpus[document_idx])

        # find stopwords
        n_docs *= stopword_df
        n_words = 0
        stopwords = set()
        for word_idx, count in _idx_idf.most_common():
            if count > n_docs:
                stopwords.add(self._vocabulary[word_idx])
            else:
                n_words += 1

        # warn if all words became stopwords (i.e. no words are allowed)
        if n_words == 0:
            warnings.warn(f'all {len(stopwords)} words are stopwords,'
                          f' perhaps try a lower stopword_df (currently {stopword_df})')
        return stopwords

    def all_words(self, document_index: int) -> Generator[str, Any, None]:
        for word_idx, count in self.corpus[document_index]:
            word = self._vocabulary[word_idx]
            for _ in range(count):
                yield word

    def unique_words(self, document_index: int) -> Generator[str, Any, None]:
        for word_idx, count in self.corpus[document_index]:
            yield self._vocabulary[word_idx]

    def num_words(self, document_index: int) -> int:
        return sum(count for _, count in self.corpus[document_index])

    def to_pickle(self, path, protocol_level=2):
        # not necessary to store `_vocabulary_to_idx` as it's just a reverse lookup table for `_vocabulary`
        with open(path, 'wb') as f:
            pickle.dump((self.corpus, self._vocabulary), f, protocol=protocol_level)
            return f.tell()

    @staticmethod
    def from_pickle(path):
        with open(path, 'rb') as f:
            corpus, vocabulary = pickle.load(f)

            return BagOfWordsCorpus(corpus=corpus,
                                    _vocabulary_to_idx={word: idx for idx, word in enumerate(vocabulary)},
                                    _vocabulary=vocabulary)
