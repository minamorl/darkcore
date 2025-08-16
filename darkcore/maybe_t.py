# filepath: darkcore/maybe_t.py
from __future__ import annotations
from typing import Callable, Generic, TypeVar, Any, Optional
from .core import Monad
from .maybe import Maybe

A = TypeVar("A")
B = TypeVar("B")


class MaybeT(Generic[A]):
    """
    MaybeT: Monad transformer for Maybe.
    実際には m (Maybe a) をラップする。
    Python の型システムでは高カインド型を表現できないので、
    run の型は緩く Monad[Any] にして mypy エラーを避けている。
    """

    def __init__(self, run: Monad[Any]) -> None:
        self.run: Monad[Any] = run

    @classmethod
    def lift(cls, monad: Monad[A]) -> MaybeT[A]:
        """
        m a -> MaybeT m a
        """
        return MaybeT(monad.bind(lambda x: monad.pure(Maybe(x)))) # type: ignore[arg-type]

    def map(self, f: Callable[[A], B]) -> MaybeT[B]:
        """
        MaybeT m a -> (a -> b) -> MaybeT m b
        """
        return MaybeT(
            self.run.bind(lambda maybe: self.run.pure(maybe.fmap(f)))
        )

    def ap(self: MaybeT[Callable[[A], B]], fa: MaybeT[A]) -> MaybeT[B]:
        """
        MaybeT m (a -> b) -> MaybeT m a -> MaybeT m b
        """
        return MaybeT(
            self.run.bind(lambda mf:
                fa.run.bind(lambda mx: self.run.pure(mf.ap(mx)))
            )
        )

    def bind(self, f: Callable[[A], MaybeT[B]]) -> MaybeT[B]:
        """
        MaybeT m a -> (a -> MaybeT m b) -> MaybeT m b
        """
        def step(maybe: Maybe[A]) -> Monad[Any]:
            if maybe.is_nothing():
                return self.run.pure(Maybe(None))
            else:
                return f(maybe.get_or_else(None)).run

        return MaybeT(self.run.bind(step))

    def __eq__(self, other: object) -> bool:
        return isinstance(other, MaybeT) and self.run == other.run

    def __repr__(self) -> str:
        return f"MaybeT({self.run!r})"
