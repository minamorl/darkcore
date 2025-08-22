from __future__ import annotations
from typing import Callable, Generic, TypeVar, cast
from .core import MonadOpsMixin

A = TypeVar("A")
B = TypeVar("B")
W = TypeVar("W")


class Writer(MonadOpsMixin[A], Generic[A, W]):
    """Writer モナド。

    ログ型 ``W`` はモノイドを想定し、デフォルトでは ``list`` を用いる。
    ``combine`` を差し替えることで他のモノイドにも対応できる。
    """

    def __init__(
        self,
        value: A,
        log: W | None = None,
        *,
        combine: Callable[[W, W], W] | None = None,
        empty: Callable[[], W] | None = None,
    ) -> None:
        self.value = value
        self.combine: Callable[[W, W], W] = combine or cast(Callable[[W, W], W], lambda a, b: a + b)
        self.empty: Callable[[], W] = empty or cast(Callable[[], W], list)
        self.log: W = log if log is not None else self.empty()

    @classmethod
    def pure(
        cls,
        value: A,
        log: W | None = None,
        *,
        combine: Callable[[W, W], W] | None = None,
        empty: Callable[[], W] | None = None,
    ) -> "Writer[A, W]":
        return cls(value, log, combine=combine, empty=empty)

    def fmap(self, f: Callable[[A], B]) -> "Writer[B, W]":
        return Writer(f(self.value), self.log, combine=self.combine, empty=self.empty)

    map = fmap

    def ap(self: "Writer[Callable[[A], B], W]", fa: "Writer[A, W]") -> "Writer[B, W]":
        return Writer(self.value(fa.value), self.combine(self.log, fa.log), combine=self.combine, empty=self.empty)

    def bind(self, f: Callable[[A], "Writer[B, W]"]) -> "Writer[B, W]":
        result = f(self.value)
        return Writer(result.value, self.combine(self.log, result.log), combine=self.combine, empty=self.empty)

    def tell(self, msg: W) -> "Writer[A, W]":
        return Writer(self.value, self.combine(self.log, msg), combine=self.combine, empty=self.empty)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Writer) and self.value == other.value and self.log == other.log

    def __repr__(self) -> str:
        return f"Writer({self.value!r}, log={self.log!r})"

