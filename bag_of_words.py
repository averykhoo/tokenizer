import math
import warnings
from collections import Counter
from dataclasses import dataclass
from dataclasses import field
from typing import Dict
from typing import Iterable
from typing import List
from typing import Set
from typing import Tuple


@dataclass
class BagOfWordsCorpus:
    # bags-of-words stored as tuples of (bow_word_ids, bow_word_counts), ordered by bow_word_count desc
    _corpus: List[Tuple[Tuple[int, ...], Tuple[int, ...]]] = field(default_factory=list)
    _seen: Dict[int, Set[int]] = field(default_factory=dict)
    _dedupe_hint: Dict[str, int] = field(default_factory=dict)

    # vocabulary: word <-> word_index
    vocabulary: List[str] = field(default_factory=list)
    _vocabulary_to_idx: Dict[str, int] = field(default_factory=dict)

    def word_to_index(self, word: str) -> int:
        # not thread safe!

        # known word
        if word in self._vocabulary_to_idx:
            return self._vocabulary_to_idx[word]

        # add word
        assert isinstance(word, str), word
        _idx = self._vocabulary_to_idx[word] = len(self.vocabulary)
        self.vocabulary.append(word)

        # double-check invariants before returning
        assert len(self._vocabulary_to_idx) == len(self.vocabulary) == _idx + 1
        assert self.vocabulary[_idx] == word, (self.vocabulary[_idx], word)  # check race condition
        return _idx

    def add_document(self, document_words: Iterable[str]) -> int:
        # not thread safe!
        _word_counts = Counter(self.word_to_index(word) for word in document_words)
        _bow = tuple(zip(*_word_counts.most_common())) if _word_counts else ((), ())

        # find duplicate if exists, and don't re-add
        _bow_hash = hash(_bow)
        for _idx in self._seen.get(_bow_hash, []):
            if self._corpus[_idx] == _bow:
                return _idx

        # add new unseen doc
        _idx = len(self._corpus)
        self._corpus.append(_bow)
        self._seen.setdefault(_bow_hash, set()).add(_idx)
        return _idx

    def word_counts(self, document_index: int, normalize: bool = False) -> Dict[str, int]:
        if normalize:
            _total_words = self.num_words(document_index)
            return {self.vocabulary[word_idx]: count / _total_words
                    for word_idx, count in zip(*self._corpus[document_index])}
        else:
            return {self.vocabulary[word_idx]: count
                    for word_idx, count in zip(*self._corpus[document_index])}

    def idf(self, document_indices: Iterable[int], add_one_smoothing: bool = True) -> Dict[str, float]:

        # count words
        _idx_idf = Counter()
        _n_docs = 0
        for document_idx in document_indices:
            _n_docs += 1
            _idx_idf.update(word_idx for word_idx in self._corpus[document_idx][0])

        # smoothing for idf
        _smooth = 1 if add_one_smoothing else 0
        _n_docs += _smooth

        # log + 1 helps avoid idf == 0 for words that exist in all docs
        return {self.vocabulary[word_idx]: math.log(_n_docs / (count + _smooth)) + 1
                for word_idx, count in _idx_idf.most_common()}

    def stopwords(self, document_indices: Iterable[int], stopword_df: float = 0.85) -> Set[str]:
        assert 0.0 < stopword_df <= 1.0

        # no stopwords if no limit
        if stopword_df == 1.0:
            return set()

        # count words
        _idx_idf = Counter()
        _n_docs = 0
        for document_idx in document_indices:
            _n_docs += 1
            _idx_idf.update(word_idx for word_idx in self._corpus[document_idx][0])

        # warn if not enough docs are given
        if 1 <= _n_docs <= 10:
            warnings.warn(f'there are only {_n_docs} documents, stopwords may not be statistically valid')

        # find stopwords
        _n_docs *= stopword_df
        _n_words = 0
        _stopwords = set()
        for word_idx, count in _idx_idf.most_common():
            if count > _n_docs:
                _stopwords.add(self.vocabulary[word_idx])
            else:
                _n_words += 1

        # warn if stopwords don't make sense
        if len(_stopwords) > _n_words == 0 and _n_docs <= 2:
            warnings.warn(f'min_n_docs for stopwords is {_n_docs},'
                          f' so all {len(_stopwords)} words are stopwords,'
                          f' you should try a lower stopword_df (currently {stopword_df})')
        elif len(_stopwords) > _n_words == 0:
            warnings.warn(f'all {len(_stopwords)} words are stopwords,'
                          f' you should try a lower stopword_df (currently {stopword_df})')
        elif len(_stopwords) > _n_words * 2:
            warnings.warn(f'there are at least 2x more stopwords ({len(_stopwords)}) than non-stopwords ({_n_words}),'
                          f' you may want to try a lower stopword_df (currently {stopword_df})')

        return _stopwords

    def words(self, document_index: int) -> List[str]:
        _words = []
        for word_idx, count in zip(*self._corpus[document_index]):
            _words.extend([self.vocabulary[word_idx]] * count)
        return _words

    def num_words(self, document_index: int) -> int:
        return sum(self._corpus[document_index][1])

    def unique_words(self, document_index: int) -> List[str]:
        return [self.vocabulary[word_idx] for word_idx in self._corpus[document_index][0]]

    def num_unique_words(self, document_index: int) -> int:
        return len(self._corpus[document_index][1])

    def __getstate__(self) -> Tuple[List[Tuple[Tuple[int, ...], Tuple[int, ...]]], List[str], Dict[str, int]]:
        return self._corpus, self.vocabulary, self._dedupe_hint

    def __setstate__(self, state: Tuple[List[Tuple[Tuple[int, ...], Tuple[int, ...]]], List[str], Dict[str, int]]):
        self._corpus, self.vocabulary, self._dedupe_hint = state

        # rebuild _seen: hash of bow -> doc_idx
        self._seen = dict()
        for _idx, _bow in enumerate(self._corpus):
            self._seen.setdefault(hash(_bow), set()).add(_idx)

        # rebuild vocab reverse lookup
        self._vocabulary_to_idx = {word: idx for idx, word in enumerate(state[1])}
