# filepath: darkcore/core.py
from __future__ import annotations
from typing import Any, Callable, Generic, Protocol, TypeVar

A = TypeVar("A")
B = TypeVar("B")


class Applicative(Protocol, Generic[A]):
    """
    構造的サブタイピングで表現した最小限の Applicative プロトコル。
    具体型（Maybe, Result, Either など）は、このプロトコルが要求する
    メソッド群（pure, ap）を実装していれば「Applicative 的」に振る舞える。
    """

    @classmethod
    def pure(cls, value: A) -> Applicative[A]:
        """値を Applicative コンテキストに持ち上げる"""
        ...

    def ap(self, fa: Applicative[Any]) -> Applicative[Any]:
        """
        self が f: (A -> B) を含む Applicative,
        fa が A を含む Applicative のとき、
        f を適用して B を含む Applicative を返す。
        """
        ...


class Monad(Protocol, Generic[A]):
    """
    構造的サブタイピングで表現した最小限の Monad プロトコル。
    ・pure: a -> m a
    ・bind: m a -> (a -> m b) -> m b
    ・fmap: m a -> (a -> b) -> m b
    HKTs が無い Python では正確な型制約ができないため Any を許容。
    """

    @classmethod
    def pure(cls, value: A) -> Monad[A]:
        """値を Monad コンテキストに持ち上げる"""
        ...

    def bind(self, f: Callable[[A], Monad[Any]]) -> Monad[Any]:
        """文脈付き値に f: a -> m b を適用して m b を返す"""
        ...

    def fmap(self, f: Callable[[A], B]) -> Monad[B]:
        """文脈付き値に純粋関数を適用して m b を返す"""
        ...
