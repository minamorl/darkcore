from __future__ import annotations
from typing import Callable, Generic, TypeVar, Any
from .core import Monad as MonadLike
from .either import Either, Left, Right

A = TypeVar("A")
B = TypeVar("B")

class EitherT(Generic[A]):
    """Monad transformer for Either.

    Wraps: m (Either a)
    """

    def __init__(self, run: MonadLike[Any]) -> None:
        self.run: MonadLike[Any] = run

    @classmethod
    def lift(cls, monad: MonadLike[A]) -> "EitherT[A]":
        """Lift a monad into EitherT."""
        return EitherT(monad.bind(lambda x: monad.pure(Right(x))))  # type: ignore[arg-type]

    def map(self, f: Callable[[A], B]) -> "EitherT[B]":
        return EitherT(self.run.bind(lambda e: self.run.pure(e.fmap(f))))

    def ap(self: "EitherT[Callable[[A], B]]", fa: "EitherT[A]") -> "EitherT[B]":
        return EitherT(self.run.bind(lambda mf: fa.run.bind(lambda mx: self.run.pure(mf.ap(mx)))))

    def bind(self, f: Callable[[A], "EitherT[B]"]) -> "EitherT[B]":
        def step(either: Either[A]) -> MonadLike[Any]:
            if isinstance(either, Left):
                return self.run.pure(either)
            else:
                return f(either.value).run
        return EitherT(self.run.bind(step))

    def __eq__(self, other: object) -> bool:
        return isinstance(other, EitherT) and self.run == other.run

    def __repr__(self) -> str:
        return f"EitherT({self.run!r})"
