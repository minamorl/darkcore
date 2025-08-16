from __future__ import annotations
from typing import Callable, Generic, TypeVar, Tuple, List

A = TypeVar("A")
B = TypeVar("B")
C = TypeVar("C")

class Writer(Generic[A]):
    def __init__(self, value: A, log: List[str] | None = None) -> None:
        self.value = value
        self.log: List[str] = log or []

    @classmethod
    def pure(cls, value: A) -> Writer[A]:
        return Writer(value, [])

    def fmap(self, f: Callable[[A], B]) -> Writer[B]:
        return Writer(f(self.value), self.log)

    def bind(self, f: Callable[[A], Writer[B]]) -> Writer[B]:
        result = f(self.value)
        return Writer(result.value, self.log + result.log)

    def tell(self, msg: str) -> Writer[A]:
        return Writer(self.value, self.log + [msg])

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Writer) and self.value == other.value and self.log == other.log

    def __repr__(self) -> str:
        return f"Writer({self.value!r}, log={self.log!r})"
