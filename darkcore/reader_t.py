from __future__ import annotations
from typing import Callable, Generic, TypeVar
from .core import Monad as MonadLike  # Protocol として使う

R = TypeVar("R")
A = TypeVar("A")
B = TypeVar("B")

class ReaderT(Generic[R, A]):
    def __init__(self, run: Callable[[R], MonadLike[A]]) -> None:
        self.run = run

    @classmethod
    def lift(cls, monad: MonadLike[A]) -> "ReaderT[R, A]":
        return ReaderT(lambda _: monad)

    @classmethod
    def pure(cls, value: A) -> "ReaderT[R, A]":
        raise NotImplementedError("ReaderT.pure not implemented (needs monad context)")

    def bind(self, f: Callable[[A], "ReaderT[R, B]"]) -> "ReaderT[R, B]":
        def new_run(env: R) -> MonadLike[B]:
            inner = self.run(env)
            return inner.bind(lambda x: f(x).run(env))
        return ReaderT(new_run)

    def __rshift__(self, f: Callable[[A], "ReaderT[R, B]"]) -> "ReaderT[R, B]":
        return self.bind(f)

    def __call__(self, env: R) -> MonadLike[A]:
        return self.run(env)

    def __repr__(self) -> str:
        return f"ReaderT({self.run!r})"
