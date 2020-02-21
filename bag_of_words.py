import math
import pickle
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
    # vocabulary: word <-> word_index
    vocabulary: List[str] = field(default_factory=list)
    _vocab_indices: Dict[str, int] = field(default_factory=dict)

    # bags-of-words stored as tuples of (bow_word_indices, bow_word_counts), ordered by bow_word_count desc
    _bow_corpus: List[Tuple[Tuple[int, ...], Tuple[int, ...]]] = field(default_factory=list)
    _bow_hash_to_idx: Dict[int, Set[int]] = field(default_factory=dict)
    _doc_id_to_idx: Dict[str, int] = field(default_factory=dict)

    def _resolve_word_index(self, word: str) -> int:

        # return if known word
        if word in self._vocab_indices:
            return self._vocab_indices[word]

        # add if unknown word
        assert isinstance(word, str), word
        _idx = self._vocab_indices[word] = len(self.vocabulary)
        self.vocabulary.append(word)

        # double-check invariants before returning
        assert len(self._vocab_indices) == len(self.vocabulary) == _idx + 1
        assert self.vocabulary[_idx] == word, (self.vocabulary[_idx], word)  # check race condition
        return _idx

    def set_document_id(self, document_id: str, document_index: int) -> int:
        assert isinstance(document_id, str), document_id
        assert isinstance(document_index, int), document_index
        assert document_index < len(self._bow_corpus)

        _document_index = self._doc_id_to_idx.setdefault(document_id, document_index)
        if _document_index != document_index:
            raise KeyError(document_id, document_index, _document_index)

        return _document_index

    def _resolve_document_id(self, document_id: Union[str, int]) -> int:

        # does document id exist?
        if isinstance(document_id, str):
            if document_id in self._doc_id_to_idx:
                return self._doc_id_to_idx[document_id]
            raise KeyError(document_id)

        # maybe its a document index?
        if isinstance(document_id, int):
            if document_id < len(self._bow_corpus):
                return document_id
            raise KeyError(document_id)

        raise TypeError(document_id)

    def _resolve_document_ids(self, document_ids: Union[str, int, Iterable[Union[str, int]]]) -> List[int]:
        if isinstance(document_ids, (str, int)):
            return [self._resolve_document_id(document_ids)]
        else:
            return [self._resolve_document_id(document_idx) for document_idx in document_ids]

    def add_document(self, document_words: Iterable[str], document_id: Optional[str] = None) -> int:
        if isinstance(document_words, str):
            raise TypeError(document_words)
        if document_id is not None:
            assert isinstance(document_id, str), document_id

            # if we the doc already exists
            if document_id in self._doc_id_to_idx:
                return self._doc_id_to_idx[document_id]

        # build bow (ordered by count desc, word_idx asc)
        _word_idx_counts = Counter(self._resolve_word_index(word) for word in document_words)
        if _word_idx_counts:
            _bow = tuple(zip(*sorted(_word_idx_counts.most_common(), key=lambda x: (-x[1], x[0]))))
        else:
            _bow = ((), ())

        # find duplicate if exists, and don't re-add
        _bow_hash = hash(_bow)
        for _document_idx in self._bow_hash_to_idx.get(_bow_hash, []):
            if self._bow_corpus[_document_idx] == _bow:
                if document_id is not None:
                    self.set_document_id(document_id, _document_idx)
                return _document_idx

        # add new unseen doc
        _document_idx = len(self._bow_corpus)
        self._bow_corpus.append(_bow)
        self._bow_hash_to_idx.setdefault(_bow_hash, set()).add(_document_idx)
        if document_id is not None:
            self.set_document_id(document_id, _document_idx)
        return _document_idx

    def word_counts(self, document_indices: Union[str, int, Iterable[Union[str, int]]],
                    normalize: bool = False
                    ) -> Dict[str, int]:

        document_indices = self._resolve_document_ids(document_indices)

        # sum over all word_idx counts
        _idx_counts = Counter()
        for _document_idx in document_indices:
            for _word_idx, _count in zip(*self._bow_corpus[_document_idx]):
                _idx_counts[_word_idx] += _count

        # calculate normalized word count (sums to 1)
        if normalize:
            _total_words = sum(_idx_counts.values())
            return {self.vocabulary[word_idx]: count / _total_words
                    for word_idx, count in _idx_counts.most_common()}

        # calculate word count
        else:
            return {self.vocabulary[word_idx]: count
                    for word_idx, count in _idx_counts.most_common()}

    def idf(self, document_indices: Iterable[Union[str, int]], add_one_smoothing: bool = True) -> Dict[str, float]:
        document_indices = self._resolve_document_ids(document_indices)

        # count words
        _idx_df = Counter()
        _n_docs = 0
        for _document_idx in document_indices:
            _n_docs += 1
            _idx_df.update(word_idx for word_idx in self._bow_corpus[_document_idx][0])

        # no docs, or no words
        # todo: warn?
        if len(_idx_df) == 0:
            return dict()

        # smoothing for idf
        _smooth = 1 if add_one_smoothing else 0
        _n_docs += _smooth

        # log + 1 helps avoid idf == 0 for words that exist in all docs
        return {self.vocabulary[word_idx]: math.log(_n_docs / (count + _smooth)) + 1
                for word_idx, count in _idx_df.most_common()}

    def stopwords(self, document_indices: Iterable[Union[str, int]], stopword_df: float = 0.85) -> Set[str]:
        document_indices = self._resolve_document_ids(document_indices)
        assert 0.0 < stopword_df <= 1.0

        # no stopwords if no limit
        if stopword_df == 1.0:
            return set()

        # count words
        _idx_df = Counter()
        _n_docs = 0
        for _document_idx in document_indices:
            _n_docs += 1
            _idx_df.update(word_idx for word_idx in self._bow_corpus[_document_idx][0])

        # warn if not enough docs are given
        if 1 <= _n_docs <= 10:
            warnings.warn(f'there are only {_n_docs} documents, stopwords may not be statistically valid')

        # find stopwords
        _n_docs *= stopword_df
        _n_words = 0
        _stopwords = set()
        for word_idx, count in _idx_df.most_common():
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

    def words(self, document_index: Union[str, int]) -> List[str]:
        # todo: apply to multiple docs?
        document_index = self._resolve_document_id(document_index)

        _words = []
        for word_idx, count in zip(*self._bow_corpus[document_index]):
            _words.extend([self.vocabulary[word_idx]] * count)
        return _words

    def num_words(self, document_index: Union[str, int]) -> int:
        # todo: apply to multiple docs?
        document_index = self._resolve_document_id(document_index)
        return sum(self._bow_corpus[document_index][1])

    def unique_words(self, document_index: Union[str, int]) -> List[str]:
        # todo: apply to multiple docs?
        document_index = self._resolve_document_id(document_index)
        return [self.vocabulary[word_idx] for word_idx in self._bow_corpus[document_index][0]]

    def num_unique_words(self, document_index: Union[str, int]) -> int:
        # todo: apply to multiple docs?
        document_index = self._resolve_document_id(document_index)
        return len(self._bow_corpus[document_index][1])

    def __getstate__(self) -> Tuple[List[Tuple[Tuple[int, ...], Tuple[int, ...]]],
                                    List[str],
                                    List[Union[None, str, Tuple[str, ...]]]]:
        _id_to_idx: List = [[] for _ in range(len(self._bow_corpus))]
        for _document_id, _document_idx in self._doc_id_to_idx.items():
            _id_to_idx[_document_idx].append(_document_id)

        _last_non_none = -1
        for _idx, _ids in enumerate(_id_to_idx):
            if len(_ids) == 0:
                _id_to_idx[_idx] = None
            elif len(_ids) == 1:
                _id_to_idx[_idx] = _id_to_idx[_idx][0]
                _last_non_none = _idx
            else:
                _id_to_idx[_idx] = tuple(_id_to_idx[_idx])
                _last_non_none = _idx
        _id_to_idx = _id_to_idx[:_last_non_none + 1]

        return self._bow_corpus, self.vocabulary, _id_to_idx

    def __setstate__(self, state: Tuple[List[Tuple[Tuple[int, ...], Tuple[int, ...]]],
                                        List[str],
                                        List[Union[None, str, Tuple[str, ...]]]]
                     ) -> 'BagOfWordsCorpus':

        # set corpus and vocab, need to unpack the id-to-idx mapping
        self._bow_corpus, self.vocabulary, _id_to_idx = state

        # rebuild _seen: hash of bow -> doc_idx
        self._bow_hash_to_idx = dict()
        for _idx, _bow in enumerate(self._bow_corpus):
            self._bow_hash_to_idx.setdefault(hash(_bow), set()).add(_idx)

        # unpack document id to idx lookup
        self._doc_id_to_idx = dict()
        for _idx, _ids in enumerate(_id_to_idx):
            if isinstance(_ids, str):
                self.set_document_id(_ids, _idx)
            elif isinstance(_ids, tuple):
                for _id in _ids:
                    self.set_document_id(_id, _idx)
            else:
                assert _ids is None

        # rebuild vocab reverse lookup
        self._vocab_indices = {word: idx for idx, word in enumerate(state[1])}

        return self

    def to_pickle(self, path, **kwargs) -> int:
        with open(path, 'wb') as f:
            pickle.dump(self, f, **kwargs)
            return f.tell()

    @staticmethod
    def from_pickle(path, **kwargs) -> 'BagOfWordsCorpus':
        with open(path, 'rb') as f:
            return pickle.load(f, **kwargs)
