import gzip
import math
import pickle
import warnings
from collections import Counter
from typing import Dict
from typing import Iterable
from typing import List
from typing import Optional
from typing import Set
from typing import Tuple
from typing import Union


class BagOfWordsCorpus:
    __slots__ = ('vocabulary', '_vocab_indices', '_bow_corpus', '_bow_hash_to_idx', '_doc_id_to_idx')

    # vocabulary: word <-> word_index
    vocabulary: List[str]  # word_index -> word
    _vocab_indices: Dict[str, int]  # word -> word_index

    # bags-of-words stored as tuples of (bow_word_indices, bow_word_counts), ordered by bow_word_count desc
    _bow_corpus: List[Tuple[Tuple[int, ...], Tuple[int, ...]]]  # doc_idx -> doc_bow
    _bow_hash_to_idx: Dict[int, Set[int]]  # bow_hash -> doc_idx
    _doc_id_to_idx: Dict[str, int]  # doc_id -> doc_idx

    def __init__(self):
        self.vocabulary = []
        self._vocab_indices = dict()
        self._bow_corpus = []
        self._bow_hash_to_idx = dict()
        self._doc_id_to_idx = dict()

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

        # assert that document_id does not already resolve to a different document_index
        _document_index = self._doc_id_to_idx.setdefault(document_id, document_index)
        if _document_index != document_index:
            raise KeyError(document_id, document_index, _document_index)

        return _document_index

    def _resolve_document_id(self, document_id: Union[str, int]) -> int:

        # document id exists?
        if isinstance(document_id, str):
            if document_id in self._doc_id_to_idx:
                return self._doc_id_to_idx[document_id]
            raise KeyError(document_id)

        # document index exists?
        if isinstance(document_id, int):
            if document_id < len(self._bow_corpus):
                return document_id
            raise KeyError(document_id)

        raise TypeError(document_id)

    def resolve_document_id(self, document_id: str) -> Optional[int]:
        try:
            return self._resolve_document_id(document_id=document_id)
        except KeyError:
            return None

    def _resolve_document_ids(self, document_ids: Union[str, int, Iterable[Union[str, int]]]) -> List[int]:

        # single id, convert to list of one item
        if isinstance(document_ids, (str, int)):
            return [self._resolve_document_id(document_ids)]

        # multiple ids (duplicate indices must be allowed because of de-duplicated bow corpus!)
        if isinstance(document_ids, Iterable):  # note that str is Iterable
            return [self._resolve_document_id(document_idx) for document_idx in document_ids]

        raise TypeError

    def add_document(self, document_words: Iterable[str], document_id: Optional[str] = None) -> int:

        # forgot to tokenize?
        if isinstance(document_words, str):
            raise TypeError(document_words)

        # check for existing document
        if document_id is not None:
            if document_id in self._doc_id_to_idx:
                return self._doc_id_to_idx[document_id]
            assert isinstance(document_id, str), document_id

        # build bow (ordered by count desc, word_idx asc)
        _word_idx_counts = Counter(self._resolve_word_index(word) for word in document_words)
        if _word_idx_counts:
            _bow = tuple(zip(*sorted(_word_idx_counts.most_common(), key=lambda x: (-x[1], x[0]))))
        else:
            _bow = ((), ())

        # if duplicate exists, return existing bow
        _bow_hash = hash(_bow)  # don't trust the hash to be unique, use linear probing later
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

    def word_counts_(self, document_indices: Union[str, int, Iterable[Union[str, int]]],
                     normalize: bool = False
                     ) -> Dict[int, int]:
        document_indices = self._resolve_document_ids(document_indices)

        # sum over all word_idx counts
        _idx_counts = Counter()
        for _document_idx in document_indices:
            for _word_idx, _count in zip(*self._bow_corpus[_document_idx]):
                _idx_counts[_word_idx] += _count

        # calculate normalized word count (sums to 1)
        if normalize:
            _total_words = sum(_idx_counts.values())
            for _word_idx, _count in _idx_counts.most_common():
                _idx_counts[_word_idx] = _count / _total_words

        return _idx_counts  # technically this is a Counter

    def word_counts(self, document_indices: Union[str, int, Iterable[Union[str, int]]],
                    normalize: bool = False
                    ) -> Dict[str, int]:
        _idx_counts = self.word_counts_(document_indices=document_indices, normalize=normalize)
        return {self.vocabulary[word_idx]: count
                for word_idx, count in _idx_counts.items()}

    def words(self, document_indices: Union[str, int, Iterable[Union[str, int]]]) -> List[str]:
        _words = []
        for _word, _count in self.word_counts(document_indices, normalize=False):
            _words.extend([_word] * _count)
        return _words

    def num_words(self, document_indices: Union[str, int, Iterable[Union[str, int]]]) -> int:
        document_indices = self._resolve_document_ids(document_indices)

        _num_words = 0
        for _document_idx in document_indices:
            _num_words += sum(self._bow_corpus[_document_idx][1])
        return _num_words

    def unique_words_(self, document_indices: Union[str, int, Iterable[Union[str, int]]]) -> List[int]:
        document_indices = self._resolve_document_ids(document_indices)

        _unique_word_indices = set()
        for _document_idx in document_indices:
            _unique_word_indices.update(self._bow_corpus[_document_idx][0])
        return sorted(_unique_word_indices)

    def unique_words(self, document_indices: Union[str, int, Iterable[Union[str, int]]]) -> List[str]:
        return [self.vocabulary[word_idx] for word_idx in self.unique_words_(document_indices)]

    def num_unique_words(self, document_indices: Union[str, int, Iterable[Union[str, int]]]) -> int:
        document_indices = self._resolve_document_ids(document_indices)

        _unique_word_indices = set()
        for _document_idx in document_indices:
            _unique_word_indices.update(self._bow_corpus[_document_idx][0])
        return len(_unique_word_indices)

    def idf_(self, document_indices: Iterable[Union[str, int]], add_one_smoothing: bool = True) -> Dict[int, float]:
        if isinstance(document_indices, (str, int)):
            raise TypeError(document_indices)
        document_indices = self._resolve_document_ids(document_indices)

        # no docs
        if len(document_indices) == 0:
            warnings.warn('no docs specified, empty idf will be returned')
            return dict()

        # only one doc, idf doesn't make sense since that's just the unique words
        if len(document_indices) == 1:
            warnings.warn(f'only one doc specified, idf is not useful')
            return {word: 1 for word in self.unique_words(document_indices[0])}  # idf == 1 with or without smoothing

        # count words
        _idx_df = Counter()
        for _document_idx in document_indices:
            _idx_df.update(word_idx for word_idx in self._bow_corpus[_document_idx][0])

        # no words, empty idf (should warn?)
        if len(_idx_df) == 0:
            return dict()

        # smoothing for idf
        _smooth = 1 if add_one_smoothing else 0
        _n_docs = len(document_indices) + _smooth

        # log + 1 helps avoid idf == 0 for words that exist in all docs
        for _word_idx, _count in _idx_df.most_common():
            _idx_df[_word_idx] = math.log(_n_docs / (_count + _smooth)) + 1

        return _idx_df  # technically this is a Counter

    def idf(self, document_indices: Iterable[Union[str, int]], add_one_smoothing: bool = True) -> Dict[str, float]:
        _idf = self.idf_(document_indices=document_indices, add_one_smoothing=add_one_smoothing)
        return {self.vocabulary[word_idx]: word_idf for word_idx, word_idf in _idf.items()}

    def stopwords_(self, document_indices: Iterable[Union[str, int]], stopword_df: float = 0.85) -> Set[int]:
        if isinstance(document_indices, (str, int)):
            raise TypeError(document_indices)
        document_indices = self._resolve_document_ids(document_indices)
        if not 0.0 < stopword_df <= 1.0:
            raise ValueError(stopword_df)

        # no stopwords if no limit
        if stopword_df == 1.0:
            warnings.warn('setting STOPWORD_DF to 1.0 means no words are stopwords')
            return set()

        # no docs
        if len(document_indices) == 0:
            warnings.warn('no docs specified, no stopwords will be returned')
            return set()

        # only one doc, idf doesn't make sense since that's just the unique words
        if len(document_indices) == 1:
            warnings.warn(f'only one doc specified, so all words are stopwords, so stopwords are not useful')
            return set(self.unique_words_(document_indices[0]))

        # warn if not enough docs are given
        if len(document_indices) <= 10:
            warnings.warn(f'there are only {len(document_indices)} documents, stopwords may not be statistically valid')

        # count words
        _idx_df = Counter()
        for _document_idx in document_indices:
            _idx_df.update(word_idx for word_idx in self._bow_corpus[_document_idx][0])

        # find stopwords
        _min_n_docs = len(document_indices) * stopword_df
        _n_words = 0
        _stopwords = set()
        for word_idx, count in _idx_df.most_common():
            if count > _min_n_docs:
                _stopwords.add(word_idx)
            else:
                _n_words += 1

        # warn if stopwords don't make sense
        if len(_stopwords) > _n_words == 0 and _min_n_docs <= 2:
            warnings.warn(f'min_n_docs for stopwords is {_min_n_docs},'
                          f' so all {len(_stopwords)} words are stopwords,'
                          f' you may want to try a higher stopword_df (currently {stopword_df}) or add more docs')
        elif len(_stopwords) > _n_words == 0:
            warnings.warn(f'all {len(_stopwords)} words are stopwords,'
                          f' you should try a higher stopword_df (currently {stopword_df}) or add more docs')
        elif len(_stopwords) > _n_words * 2:
            warnings.warn(f'there are at least 2x more stopwords ({len(_stopwords)}) than non-stopwords ({_n_words}),'
                          f' you may want to try a higher stopword_df (currently {stopword_df}) or add more docs')

        return _stopwords

    def stopwords(self, document_indices: Iterable[Union[str, int]], stopword_df: float = 0.85) -> Set[str]:
        _stopword_indices = self.stopwords_(document_indices=document_indices, stopword_df=stopword_df)
        return set(self.vocabulary[word_idx] for word_idx in _stopword_indices)

    def __getstate__(self) -> Tuple[List[Tuple[Tuple[int, ...], Tuple[int, ...]]],
                                    List[str],
                                    List[Union[None, str, Tuple[str, ...]]]]:

        # shuffle the `_doc_id_to_idx` lookup table into a list (matching the corpus index)
        _id_to_idx: List = [[] for _ in range(len(self._bow_corpus))]
        for _document_id, _document_idx in self._doc_id_to_idx.items():
            _id_to_idx[_document_idx].append(_document_id)

        # more compact representation than a list of lists,  andtruncated as short as possible
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

        # don't need the other lookup tables
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

    def to_gzip(self, path, *, pickle_protocol=4) -> int:
        with gzip.open(path, 'wb') as f:
            pickle.dump(self, f, protocol=pickle_protocol)
            return f.tell()

    @staticmethod
    def from_gzip(path) -> 'BagOfWordsCorpus':
        with gzip.open(path, 'rb') as f:
            return pickle.load(f)
