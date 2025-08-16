# filepath: darkcore/core.py
from __future__ import annotations
from typing import Callable, TypeVar, Generic, Self
from abc import ABC, abstractmethod

A = TypeVar("A")
B = TypeVar("B")


class Applicative(ABC, Generic[A]):
    @classmethod
    @abstractmethod
    def pure(cls, value: A) -> Self:
        """
        Lift a value into the minimal applicative context.
        """
        raise NotImplementedError

    @abstractmethod
    def ap(self, fa: Self) -> Self:
        """
        Apply a wrapped function `self: f (a -> b)` to another applicative `fa: f a`,
        producing `f b`.
        """
        raise NotImplementedError

    # Operator: Haskell's <*>
    def __matmul__(self, fa: Self) -> Self:
        return self.ap(fa)


class Monad(Applicative[A], ABC, Generic[A]):
    """
    Monad: Extension of Applicative.
    - pure :: a -> m a
    - bind :: m a -> (a -> m b) -> m b
    """

    @classmethod
    @abstractmethod
    def pure(cls, value: A) -> Self:
        """
        Lift a value into the monadic context.
        """
        raise NotImplementedError

    @abstractmethod
    def bind(self, f: Callable[[A], Self]) -> Self:
        """
        Given self: m a, apply f: a -> m b to produce m b.
        """
        raise NotImplementedError

    # Operator: Haskell's >>=
    def __rshift__(self, f: Callable[[A], Self]) -> Self:
        return self.bind(f)

    # Operator: Haskell's <$>
    def __or__(self, f: Callable[[A], B]) -> Monad[B]:  # type: ignore
        # default fmap via bind+pure
        return self.bind(lambda x: self.pure(f(x)))  # type: ignore
