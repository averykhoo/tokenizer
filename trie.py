from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from typing import Dict
from typing import Optional
from typing import Type


class Match:
    def __init__(self, start, end, match):
        self.regs = ((start, end),)  # mimic the re.Match object
        self.str = match  # re.Match stores a reference to the ENTIRE ORIGINAL STRING, let's not do that

    __slots__ = ('regs', 'str')

    def group(self, group_index=0):
        return self[group_index]

    def start(self, group_index=0):
        if group_index != 0:
            raise IndexError('no such group')
        return self.regs[0][0]

    def end(self, group_index=0):
        if group_index != 0:
            raise IndexError('no such group')
        return self.regs[0][1]

    def span(self, group_index=0):
        if group_index != 0:
            raise IndexError('no such group')
        return self.regs[0]

    def __getitem__(self, group_index):
        if group_index != 0:
            raise IndexError('no such group')
        return self.str

    def __repr__(self):
        return f'<Match object; span={self.regs[0]}, match={repr(self.str)}>'


@dataclass
class Node:  # todo: implement `__slots__`, subclass `dict`
    length: int
    next: Dict[str, Type['Node']]
    replacement: Optional[str]
    fail: Optional[Type['Node']] = None
    match: Optional[Type['Node']] = None


class Trie(ABC):
    len: int
    root: Node

    __slots__ = ('len', 'root')

    @abstractmethod
    def __contains__(self, key):
        pass

    def __len__(self):
        return self.len

    @abstractmethod
    def keys(self):
        pass

    @abstractmethod
    def values(self):
        pass

    @abstractmethod
    def __getitem__(self, key):
        pass

    @abstractmethod
    def pop(self, key=None):
        pass

    @abstractmethod
    def get(self, key, default=None):
        pass

    @abstractmethod
    def __set__(self, key, value):
        pass

    @abstractmethod
    def __delitem__(self, key):
        pass

    @abstractmethod
    def setdefault(self, key, value):
        pass

    @abstractmethod
    def finditer(self, text):
        pass

    @abstractmethod
    def findall(self, text):
        pass

    @abstractmethod
    def sub(self, text):
        pass

    @abstractmethod
    def items(self):
        pass
