from typing import Callable, TypeVar, Generic
from abc import ABC, abstractmethod

A = TypeVar('A', covariant=True)
B = TypeVar('B')
C = TypeVar('C')
D = TypeVar('D')


class Functor(ABC, Generic[C]):
    @abstractmethod
    def fmap(self, f: Callable[[C], B]) -> 'Functor[B]':
        pass


class Applicative(Functor[C], ABC, Generic[C]):
    @staticmethod
    @abstractmethod
    def pure(value: C) -> 'Applicative[C]':
        pass

    @abstractmethod
    def ap(self, ff: 'Applicative[Callable[[C], B]]') -> 'Applicative[B]':
        pass


class Monad(Applicative[C], ABC, Generic[C]):
    @staticmethod
    @abstractmethod
    def pure(value: C) -> 'Monad[C]':
        pass

    @abstractmethod
    def bind(self, f: Callable[[C], 'Monad[B]']) -> 'Monad[B]':
        pass
