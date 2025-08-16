from __future__ import annotations
from typing import Callable, Generic, TypeVar
from .core import Monad

A = TypeVar("A")
B = TypeVar("B")

class Result(Monad[A], Generic[A]):
    def map(self, f: Callable[[A], B]) -> Result[B]:
        return self.fmap(f)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Result) and self.__dict__ == other.__dict__


class Ok(Result[A]):
    def __init__(self, value: A) -> None:
        self.value = value

    @classmethod
    def pure(cls, value: A) -> Ok[A]:
        return Ok(value)

    def fmap(self, f: Callable[[A], B]) -> Ok[B]:
        return Ok(f(self.value))

    def bind(self, f: Callable[[A], Result[B]]) -> Result[B]:
        return f(self.value)

    def __repr__(self) -> str:
        return f"Ok({self.value!r})"

    def ap(self, fa: Result[A]) -> Result[B]:
        if isinstance(fa, Ok):
            if callable(self.value):
                return Ok(self.value(fa.value))  # type: ignore
            raise TypeError("Ok.ap expects a callable in self.value")
        return fa


class Err(Result[A]):
    def __init__(self, error: str) -> None:
        self.error = error

    @classmethod
    def pure(cls, value: A) -> Ok[A]:
        return Ok(value)

    def fmap(self, f: Callable[[A], B]) -> Err[A]:
        return self

    def bind(self, f: Callable[[A], Result[B]]) -> Err[A]:
        return self

    def __repr__(self) -> str:
        return f"Err({self.error!r})"

    def ap(self, fa: Result[A]) -> Err[A]:
        return self
