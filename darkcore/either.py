from __future__ import annotations
from typing import Callable, Generic, TypeVar, Union
from .core import Monad

A = TypeVar("A")
B = TypeVar("B")

class Either(Monad[A], Generic[A]):
    def map(self, f: Callable[[A], B]) -> Either[B]:
        return self.fmap(f)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Either) and self.__dict__ == other.__dict__


class Left(Either[A]):
    def __init__(self, value: A) -> None:
        self.value = value

    @classmethod
    def pure(cls, value: A) -> Right[A]:  # Left.pure は常に Right
        return Right(value)

    def fmap(self, f: Callable[[A], B]) -> Left[A]:
        return self

    def bind(self, f: Callable[[A], Either[B]]) -> Left[A]:
        return self

    def ap(self, fa: Either[A]) -> Left[A]:
        return self

    def __repr__(self) -> str:
        return f"Left({self.value!r})"


class Right(Either[A]):
    def __init__(self, value: A) -> None:
        self.value = value

    @classmethod
    def pure(cls, value: A) -> Right[A]:
        return Right(value)

    def fmap(self, f: Callable[[A], B]) -> Right[B]:
        return Right(f(self.value))

    def bind(self, f: Callable[[A], Either[B]]) -> Either[B]:
        return f(self.value)

    def ap(self, fa: Either[A]) -> Either[B]:
        if isinstance(fa, Right):
            if callable(self.value):
                return Right(self.value(fa.value))  # type: ignore
            raise TypeError("Right.ap expects a callable in self.value")
        return fa

    def __repr__(self) -> str:
        return f"Right({self.value!r})"
