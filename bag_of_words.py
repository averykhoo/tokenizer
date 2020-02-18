import pickle
from collections import Counter
from dataclasses import dataclass, field
from typing import Tuple, Dict, List


@dataclass
class BagOfWordsCorpus:
    corpus: List[Tuple[Tuple[int, int], ...]] = field(default_factory=dict)
    vocabulary_lookup: Dict[str, int] = field(default_factory=dict)
    vocabulary_words: List[str] = field(default_factory=list)

    def add(self, document_words):
        c = Counter(self.vocabulary(word) for word in document_words)
        # todo: thread safe?
        self.corpus.append(tuple(c.most_common()))
        return len(self.corpus) - 1  # this is the document_idx

    def words(self, document_idx):
        for word_idx, count in self.corpus[document_idx]:
            word = self.vocabulary_words[word_idx]
            for _ in range(count):
                yield word

    def tf(self, document_idx):
        return {self.vocabulary_lookup[word_idx]: count
                for word_idx, count in self.corpus[document_idx]}

    def idf(self, document_idxs):
        c = Counter()
        for document_idx in document_idxs:
            c.update(self.unique_words(document_idx))
        return c

    def unique_words(self, document_idx):
        for word_idx, count in self.corpus[document_idx]:
            yield self.vocabulary_words[word_idx]

    def len(self, document_idx):
        return sum(count for _, count in self.corpus[document_idx])

    def vocabulary(self, item):
        # todo: make this work
        if isinstance(item, str):
            return self.vocabulary_lookup[item]
        elif isinstance(item, int):
            return self.vocabulary_words[item]

    def to_pickle(self, path, protocol_level=2):
        with open(path, 'wb') as f:
            pickle.dump((self.corpus, self.vocabulary_lookup, self.vocabulary_words), f, protocol=protocol_level)
            return f.tell()

    @staticmethod
    def from_pickle(path):
        with open(path, 'rb') as f:
            corpus, vocab_lookup, vocab_words = pickle.load(f)
            return BagOfWordsCorpus(corpus=corpus, vocabulary_lookup=vocab_lookup, vocabulary_words=vocab_words)
