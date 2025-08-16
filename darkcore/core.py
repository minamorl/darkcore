from typing import Callable, TypeVar, Generic, Protocol, runtime_checkable, Self
from abc import ABC, abstractmethod

A = TypeVar("A")
B = TypeVar("B")


class Applicative(ABC, Generic[A]):
    @classmethod
    @abstractmethod
    def pure(cls, value: A) -> Self:
        """
        値を最小限のコンテキストに持ち上げる。
        """
        raise NotImplementedError

    @abstractmethod
    def ap(self, fa: Self) -> Self:
        """
        self が f (a -> b) を保持しているとき、fa: f a を適用し f b を返す。
        """
        raise NotImplementedError


class Monad(Applicative[A], ABC, Generic[A]):
    """
    Monad: Applicative の拡張。
    - pure :: a -> m a
    - bind :: m a -> (a -> m b) -> m b
    """

    @classmethod
    @abstractmethod
    def pure(cls, value: A) -> Self:
        """
        値をモナドのコンテキストに持ち上げる。
        """
        raise NotImplementedError

    @abstractmethod
    def bind(self, f: Callable[[A], Self]) -> Self:
        """
        self が m a を保持しているとき、f: a -> m b を適用し m b を返す。
        """
        raise NotImplementedError
