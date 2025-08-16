from __future__ import annotations
from typing import Callable, Generic, TypeVar, Any, cast
from .core import Monad

A = TypeVar("A")
B = TypeVar("B")


class Either(Monad[A], Generic[A]):
    # fmap は具象側で実装
    def fmap(self, f: Callable[[A], B]) -> "Either[B]":
        raise NotImplementedError

    def map(self, f: Callable[[A], B]) -> "Either[B]":
        return self.fmap(f)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Either) and self.__dict__ == other.__dict__


class Left(Either[A]):
    def __init__(self, value: A) -> None:
        self.value = value

    @classmethod
    def pure(cls, value: A) -> "Either[A]":
        # Left.pure は Right に持ち上げるのが通例
        return Right(value)

    def fmap(self, f: Callable[[A], B]) -> "Either[B]":
        return cast(Either[B], self)

    def bind(self, f: Callable[[A], Monad[B]]) -> Monad[B]:
        return cast(Monad[B], self)

    def ap(self, fa: "Either[A]") -> "Either[B]":
        return cast(Either[B], self)

    def __repr__(self) -> str:
        return f"Left({self.value!r})"


class Right(Either[A]):
    def __init__(self, value: A) -> None:
        self.value = value

    @classmethod
    def pure(cls, value: A) -> "Either[A]":
        return Right(value)

    def fmap(self, f: Callable[[A], B]) -> "Either[B]":
        return Right(f(self.value))

    # 基底 Monad と同じシグネチャ
    def bind(self, f: Callable[[A], Monad[B]]) -> Monad[B]:
        return f(self.value)

    def ap(self: "Right[Callable[[A], B]]", fa: "Either[A]") -> "Either[B]":
        if isinstance(fa, Right):
            func = self.value  # Callable[[A], B]
            return Right(func(fa.value))
        return cast(Either[B], fa)  # Left はそのまま伝播

    def __repr__(self) -> str:
        return f"Right({self.value!r})"
