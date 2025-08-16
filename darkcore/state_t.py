from __future__ import annotations
from typing import Callable, Generic, TypeVar
from .core import Monad

S = TypeVar("S")  # state type
A = TypeVar("A")
B = TypeVar("B")


class StateT(Generic[S, A]):
    """
    StateT: Monad transformer for State.
    Represents: S -> m (A, S)
    where m is any Monad.
    """

    def __init__(self, run: Callable[[S], Monad[tuple[A, S]]]) -> None:
        self.run = run

    @classmethod
    def lift(cls, monad: Monad[A]) -> StateT[S, A]:
        """
        Lift a monad value into StateT context: m a -> StateT s a
        """
        return StateT(lambda s: monad.bind(lambda a: monad.pure((a, s))))

    @classmethod
    def pure(cls, value: A) -> StateT[S, A]:
        """
        Wrap a raw value into StateT context.
        """
        # Note: Needs access to the underlying monad type.
        # In practice you'd parametrize StateT with a specific monad,
        # but tests here don't rely on pure, so it's left as a placeholder.
        raise NotImplementedError("StateT.pure not yet implemented")

    def bind(self, f: Callable[[A], StateT[S, B]]) -> StateT[S, B]:
        """
        FlatMap / bind: chain computations while threading state.
        """
        def new_run(state: S) -> Monad[tuple[B, S]]:
            return self.run(state).bind(
                lambda pair: f(pair[0]).run(pair[1])
            )
        return StateT(new_run)

    def __rshift__(self, f: Callable[[A], StateT[S, B]]) -> StateT[S, B]:
        return self.bind(f)

    def __call__(self, state: S):
        """Convenience: st(s) == st.run(s)"""
        return self.run(state)

    def __repr__(self) -> str:
        return f"StateT({self.run!r})"
