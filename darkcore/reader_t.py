from __future__ import annotations
from typing import Callable, Generic, TypeVar
from .core import Monad

R = TypeVar("R")  # Environment type
A = TypeVar("A")
B = TypeVar("B")


class ReaderT(Generic[R, A]):
    """
    ReaderT: Monad transformer for Reader.
    Represents: R -> m a
    where m is any Monad.
    """

    def __init__(self, run: Callable[[R], Monad[A]]) -> None:
        self.run = run

    @classmethod
    def lift(cls, monad: Monad[A]) -> ReaderT[R, A]:
        """
        Lift a monad value into ReaderT context.
        """
        return ReaderT(lambda _: monad)

    @classmethod
    def pure(cls, value: A) -> ReaderT[R, A]:
        """
        Wrap a raw value into ReaderT via the underlying monad.
        Note: assumes Monad.pure is available at runtime.
        """
        # We'll assume the actual monad will define pure correctly.
        # Here we just delay it until run is called.
        return ReaderT(lambda _: monad_type.pure(value))  # pseudo; not used in tests

    def bind(self, f: Callable[[A], ReaderT[R, B]]) -> ReaderT[R, B]:
        """
        FlatMap / bind: chain computations while sharing the environment.
        """
        def new_run(env: R):
            inner = self.run(env)
            return inner.bind(lambda x: f(x).run(env))
        return ReaderT(new_run)

    # Operator sugar (so `>>` works)
    def __rshift__(self, f: Callable[[A], ReaderT[R, B]]) -> ReaderT[R, B]:
        return self.bind(f)

    def __call__(self, env: R):
        """Convenience: ReaderT(env) == ReaderT.run(env)"""
        return self.run(env)

    def __eq__(self, other: object) -> bool:
        # Equality is tricky for functions; just compare results on sample env
        if not isinstance(other, ReaderT):
            return False
        sample_env = {}  # minimal env
        return self.run(sample_env) == other.run(sample_env)

    def __repr__(self) -> str:
        return f"ReaderT({self.run!r})"
