from __future__ import annotations
from typing import Callable, Generic, TypeVar

A = TypeVar("A")
B = TypeVar("B")
C = TypeVar("C")


class Reader(Generic[A, B]):
    def __init__(self, run: Callable[[A], B]) -> None:
        self.run = run

    @classmethod
    def pure(cls, value: B) -> Reader[A, B]:
        return Reader(lambda _: value)

    def bind(self, f: Callable[[B], Reader[A, C]]) -> Reader[A, C]:
        return Reader(lambda r: f(self.run(r)).run(r))
