from __future__ import annotations
from typing import Callable, Generic, TypeVar, Any
from .core import Monad as MonadLike
from .maybe import Maybe

A = TypeVar("A")
B = TypeVar("B")

class MaybeT(Generic[A]):
    """
    Wraps: m (Maybe a)
    """
    def __init__(self, run: MonadLike[Any]) -> None:
        self.run: MonadLike[Any] = run

    @classmethod
    def lift(cls, monad: MonadLike[A]) -> "MaybeT[A]":
        return MaybeT(monad.bind(lambda x: monad.pure(Maybe(x))))  # type: ignore[arg-type]

    def fmap(self, f: Callable[[A], B]) -> "MaybeT[B]":
        return MaybeT(self.run.bind(lambda maybe: self.run.pure(maybe.fmap(f))))

    map = fmap

    def ap(self: "MaybeT[Callable[[A], B]]", fa: "MaybeT[A]") -> "MaybeT[B]":
        return MaybeT(self.run.bind(lambda mf: fa.run.bind(lambda mx: self.run.pure(mf.ap(mx)))))

    def bind(self, f: Callable[[A], "MaybeT[B]"]) -> "MaybeT[B]":
        def step(maybe: Maybe[A]) -> MonadLike[Any]:
            if maybe.is_nothing():
                return self.run.pure(Maybe(None))
            else:
                return f(maybe.get_or_else(None)).run
        return MaybeT(self.run.bind(step))

    def __eq__(self, other: object) -> bool:
        return isinstance(other, MaybeT) and self.run == other.run

    def __repr__(self) -> str:
        return f"MaybeT({self.run!r})"
