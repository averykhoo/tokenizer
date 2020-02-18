import pickle
from dataclasses import dataclass, field
from typing import Tuple, Dict, List


@dataclass
class BagOfWordsCorpus:
    corpus: Dict[str, Tuple[Tuple[int, int], ...]] = field(default_factory=dict)
    vocabulary_lookup: Dict[str, int] = field(default_factory=dict)
    vocabulary_words: List[str] = field(default_factory=list)

    def add(self, document):
        pass

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
