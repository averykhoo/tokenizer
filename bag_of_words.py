import math
import warnings
from collections import Counter
from dataclasses import dataclass
from dataclasses import field
from typing import Dict
from typing import Iterable
from typing import List
from typing import Optional
from typing import Set
from typing import Tuple
from typing import Union


@dataclass
class BagOfWordsCorpus:
    # bags-of-words stored as tuples of (bow_word_ids, bow_word_counts), ordered by bow_word_count desc
    _corpus: List[Tuple[Tuple[int, ...], Tuple[int, ...]]] = field(default_factory=list)
    _seen: Dict[int, Set[int]] = field(default_factory=dict)
    _document_id_to_idx: Dict[str, int] = field(default_factory=dict)

    # vocabulary: word <-> word_index
    vocabulary: List[str] = field(default_factory=list)
    _vocabulary_to_idx: Dict[str, int] = field(default_factory=dict)

    def word_to_index(self, word: str) -> int:

        # return if known word
        if word in self._vocabulary_to_idx:
            return self._vocabulary_to_idx[word]

        # add if unknown word
        assert isinstance(word, str), word
        _idx = self._vocabulary_to_idx[word] = len(self.vocabulary)
        self.vocabulary.append(word)

        # double-check invariants before returning
        assert len(self._vocabulary_to_idx) == len(self.vocabulary) == _idx + 1
        assert self.vocabulary[_idx] == word, (self.vocabulary[_idx], word)  # check race condition
        return _idx

    def set_document_id(self, document_id: str, document_index: int) -> int:
        assert isinstance(document_id, str), document_id
        assert isinstance(document_index, int), document_index
        assert document_index < len(self._corpus)

        _document_index = self._document_id_to_idx.setdefault(document_id, document_index)
        if _document_index != document_index:
            raise KeyError(document_id, document_index, _document_index)

        return _document_index

    def _resolve_document_id(self, document_id: Union[str, int]) -> int:

        # does document id exist?
        if isinstance(document_id, str) and document_id in self._document_id_to_idx:
            return self._document_id_to_idx[document_id]

        # maybe its a document index?
        if isinstance(document_id, int) and document_id < len(self._corpus):
            return document_id

        raise KeyError(document_id)

    def add_document(self, document_words: Iterable[str], document_id: Optional[str] = None) -> int:
        if document_id is not None:
            assert isinstance(document_id, str), document_id

            # if we the doc already exists
            if document_id in self._document_id_to_idx:
                return self._document_id_to_idx[document_id]

        # build bow (ordered by count desc, word_idx asc)
        _word_idx_counts = Counter(self.word_to_index(word) for word in document_words)
        if _word_idx_counts:
            _bow = tuple(zip(*sorted(_word_idx_counts.most_common(), key=lambda w, c: (-c, w))))
        else:
            _bow = ((), ())

        # find duplicate if exists, and don't re-add
        _bow_hash = hash(_bow)
        for _document_idx in self._seen.get(_bow_hash, []):
            if self._corpus[_document_idx] == _bow:
                if document_id is not None:
                    self.set_document_id(document_id, _document_idx)
                return _document_idx

        # add new unseen doc
        _document_idx = len(self._corpus)
        self._corpus.append(_bow)
        self._seen.setdefault(_bow_hash, set()).add(_document_idx)
        if document_id is not None:
            self.set_document_id(document_id, _document_idx)
        return _document_idx

    def word_counts(self, document_index: int, normalize: bool = False) -> Dict[str, int]:
        document_index = self._resolve_document_id(document_index)

        # calculate normalized word count (sums to 1)
        if normalize:
            _total_words = self.num_words(document_index)
            return {self.vocabulary[word_idx]: count / _total_words
                    for word_idx, count in zip(*self._corpus[document_index])}

        # calculate word count
        else:
            return {self.vocabulary[word_idx]: count
                    for word_idx, count in zip(*self._corpus[document_index])}

    def idf(self, document_indices: Iterable[int], add_one_smoothing: bool = True) -> Dict[str, float]:
        document_indices = [self._resolve_document_id(document_idx) for document_idx in document_indices]

        # count words
        _idx_idf = Counter()
        _n_docs = 0
        for _document_idx in document_indices:
            _n_docs += 1
            _idx_idf.update(word_idx for word_idx in self._corpus[_document_idx][0])

        # no docs, or no words
        if len(_idx_idf) == 0:
            return dict()

        # smoothing for idf
        _smooth = 1 if add_one_smoothing else 0
        _n_docs += _smooth

        # log + 1 helps avoid idf == 0 for words that exist in all docs
        return {self.vocabulary[word_idx]: math.log(_n_docs / (count + _smooth)) + 1
                for word_idx, count in _idx_idf.most_common()}

    def stopwords(self, document_indices: Iterable[int], stopword_df: float = 0.85) -> Set[str]:
        document_indices = [self._resolve_document_id(document_idx) for document_idx in document_indices]
        assert 0.0 < stopword_df <= 1.0

        # no stopwords if no limit
        if stopword_df == 1.0:
            return set()

        # count words
        _idx_idf = Counter()
        _n_docs = 0
        for _document_idx in document_indices:
            _n_docs += 1
            _idx_idf.update(word_idx for word_idx in self._corpus[_document_idx][0])

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
        document_index = self._resolve_document_id(document_index)

        _words = []
        for word_idx, count in zip(*self._corpus[document_index]):
            _words.extend([self.vocabulary[word_idx]] * count)
        return _words

    def num_words(self, document_index: int) -> int:
        document_index = self._resolve_document_id(document_index)
        return sum(self._corpus[document_index][1])

    def unique_words(self, document_index: int) -> List[str]:
        document_index = self._resolve_document_id(document_index)
        return [self.vocabulary[word_idx] for word_idx in self._corpus[document_index][0]]

    def num_unique_words(self, document_index: int) -> int:
        document_index = self._resolve_document_id(document_index)
        return len(self._corpus[document_index][1])

    def __getstate__(self) -> Tuple[List[Tuple[Tuple[int, ...], Tuple[int, ...]]], List[str], Dict[str, int]]:
        _id_to_idx: List = [[] for _ in range(len(self._corpus))]
        for _document_id, _document_idx in self._document_id_to_idx.items():
            _id_to_idx[_document_idx].append(_document_id)

        for _idx, _ids in enumerate(_id_to_idx):
            if len(_ids) == 0:
                _id_to_idx[_idx] = None
            elif len(_ids) == 1:
                _id_to_idx[_idx] = _id_to_idx[_idx][0]
            else:
                _id_to_idx[_idx] = tuple(_id_to_idx[_idx])

        return self._corpus, self.vocabulary, self._document_id_to_idx

    def __setstate__(self, state: Tuple[List[Tuple[Tuple[int, ...], Tuple[int, ...]]], List[str], Dict[str, int]]):
        self._corpus, self.vocabulary, _id_to_idx = state

        # rebuild _seen: hash of bow -> doc_idx
        self._seen = dict()
        for _idx, _bow in enumerate(self._corpus):
            self._seen.setdefault(hash(_bow), set()).add(_idx)

        # rebuild document id lookup
        self._document_id_to_idx = dict()
        for _idx, _ids in enumerate(_id_to_idx):
            if isinstance(_ids, str):
                self.set_document_id(_ids, _idx)
            elif isinstance(_ids, tuple):
                for _id in _ids:
                    self.set_document_id(_id, _idx)
            else:
                assert _ids is None

        # rebuild vocab reverse lookup
        self._vocabulary_to_idx = {word: idx for idx, word in enumerate(state[1])}
