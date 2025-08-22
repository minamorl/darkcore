from __future__ import annotations
from typing import Callable, Generic, Optional, TypeVar
from .core import MonadOpsMixin

A = TypeVar("A")
B = TypeVar("B")

class Maybe(MonadOpsMixin[A], Generic[A]):
    __slots__ = ("_value",)

    def __init__(self, value: Optional[A]) -> None:
        self._value = value

    @classmethod
    def pure(cls, value: A) -> "Maybe[A]":
        return cls(value)

    def fmap(self, f: Callable[[A], B]) -> "Maybe[B]":
        if self._value is None:
            return Maybe(None)
        return Maybe(f(self._value))

    map = fmap  # alias

    def ap(self: "Maybe[Callable[[A], B]]", fa: "Maybe[A]") -> "Maybe[B]":
        if self._value is None or fa._value is None:
            return Maybe(None)
        return Maybe(self._value(fa._value))

    def bind(self, f: Callable[[A], "Maybe[B]"]) -> "Maybe[B]":
        if self._value is None:
            return Maybe(None)
        return f(self._value)

    def is_nothing(self) -> bool:
        return self._value is None

    def is_just(self) -> bool:
        return self._value is not None

    def get_or_else(self, default: Optional[A]) -> A:
        if self._value is None:
            return default  # type: ignore[return-value]
        return self._value

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Maybe) and self._value == other._value

    def __repr__(self) -> str:
        return "Nothing" if self._value is None else f"Just({self._value!r})"
