from __future__ import annotations
from typing import Callable, Generic, TypeVar
from .core import MonadOpsMixin

A = TypeVar("A")
B = TypeVar("B")
C = TypeVar("C")


class Reader(MonadOpsMixin[B], Generic[A, B]):
    def __init__(self, run: Callable[[A], B]) -> None:
        self.run = run

    @classmethod
    def pure(cls, value: B) -> "Reader[A, B]":
        return Reader(lambda _: value)

    def fmap(self, f: Callable[[B], C]) -> "Reader[A, C]":
        return Reader(lambda r: f(self.run(r)))

    map = fmap

    def ap(self: "Reader[A, Callable[[B], C]]", fa: "Reader[A, B]") -> "Reader[A, C]":
        return Reader(lambda r: self.run(r)(fa.run(r)))

    def bind(self, f: Callable[[B], "Reader[A, C]"]) -> "Reader[A, C]":
        return Reader(lambda r: f(self.run(r)).run(r))
