# filepath: darkcore/writer_t.py
from __future__ import annotations
from typing import Generic, TypeVar, List
from .core import Monad

A = TypeVar("A")
B = TypeVar("B")
W = TypeVar("W")  # log type (monoid)


class WriterT(Generic[A, W]):
    """
    WriterT: Monad transformer for Writer.
    Represents: m (a, w)
    where m is any Monad, and w is a monoid (e.g., list[str]).
    """

    def __init__(self, run: Monad[tuple[A, List[W]]]) -> None:
        self.run = run

    @classmethod
    def lift(cls, monad: Monad[A], empty_log: List[W]) -> WriterT[A, W]:
        """
        Lift a monad value into WriterT context: m a -> m (a, w)
        """
        return WriterT(monad.bind(lambda a: monad.pure((a, empty_log))))

    def bind(self, f: callable[[A], WriterT[B, W]]) -> WriterT[B, W]:
        """
        FlatMap: chain computations and combine logs.
        """
        def step(pair: tuple[A, List[W]]):
            (a, log1) = pair
            return f(a).run.bind(lambda res: self.run.pure((res[0], log1 + res[1])))

        return WriterT(self.run.bind(step))

    def __rshift__(self, f: callable[[A], WriterT[B, W]]) -> WriterT[B, W]:
        return self.bind(f)

    def __repr__(self) -> str:
        return f"WriterT({self.run!r})"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, WriterT) and self.run == other.run
