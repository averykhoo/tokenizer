import pickle
from collections import Counter
from dataclasses import dataclass
from dataclasses import field
from typing import Any
from typing import Dict
from typing import Generator
from typing import Iterable
from typing import List
from typing import Tuple

from tokenizer import unicode_tokenize


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

    def add_document_text(self, document: str) -> int:
        # not thread safe!
        c = Counter(self.word_to_index(word) for word in unicode_tokenize(document, words_only=True))
        self.corpus.append(tuple(c.most_common()))
        return len(self.corpus) - 1  # this is the document index

    def words(self, document_index: int) -> Generator[str, Any, None]:
        for word_idx, count in self.corpus[document_index]:
            word = self._vocabulary[word_idx]
            for _ in range(count):
                yield word

    def tf(self, document_index: int) -> Dict[str, int]:
        # todo: smoothing like TfidfVectorizer
        return {self._vocabulary[word_idx]: count for word_idx, count in self.corpus[document_index]}

    def idf(self, document_indices: Iterable[int]) -> Dict[str, int]:
        # todo: smoothing like TfidfVectorizer
        _idx_idf = Counter()
        for document_idx in document_indices:
            _idx_idf.update(word_idx for word_idx, _ in self.corpus[document_idx])
        return {self._vocabulary[word_idx]: count for word_idx, count in _idx_idf}

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
