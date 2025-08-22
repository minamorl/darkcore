from __future__ import annotations
from typing import Callable, Generic, TypeVar, Any, cast
from .core import Monad

S = TypeVar("S")  # state
A = TypeVar("A")
B = TypeVar("B")

class StateT(Generic[S, A]):
    """
    StateT m a ≅ S -> m (a, S)
    """
    def __init__(self, run: Callable[[S], Monad[tuple[A, S]]]) -> None:
        self.run = run

    @classmethod
    def lift(cls, monad: Monad[A]) -> "StateT[S, A]":
        """
        m a -> StateT m a
        実装: s ↦ monad.bind(lambda a: monad.pure((a, s)))
        mypy に多相性が伝わらないため cast で橋渡し。
        """
        def run(s: S) -> Monad[tuple[A, S]]:
            def step(a: A) -> Monad[tuple[A, S]]:
                return cast(Monad[tuple[A, S]], cast(Any, monad).pure((a, s)))
            return monad.bind(step)
        return StateT(run)

    @classmethod
    def pure_with(
        cls, pure: Callable[[tuple[A, S]], Monad[tuple[A, S]]], value: A
    ) -> "StateT[S, A]":
        """Construct ``StateT`` with provided ``pure`` (workaround for lack of HKTs)."""
        return StateT(lambda s: pure((value, s)))

    def fmap(self, f: Callable[[A], B]) -> "StateT[S, B]":
        def new_run(s: S) -> Monad[tuple[B, S]]:
            return self.run(s).fmap(lambda pair: (f(pair[0]), pair[1]))
        return StateT(new_run)

    map = fmap

    def ap(self: "StateT[S, Callable[[A], B]]", fa: "StateT[S, A]") -> "StateT[S, B]":
        def new_run(s: S) -> Monad[tuple[B, S]]:
            return self.run(s).bind(
                lambda pair_f: fa.run(pair_f[1]).bind(
                    lambda pair_a: cast(
                        Monad[tuple[B, S]],
                        cast(Any, fa.run(pair_f[1])).pure(
                            (pair_f[0](pair_a[0]), pair_a[1])
                        ),
                    )
                )
            )
        return StateT(new_run)

    def bind(self, f: Callable[[A], "StateT[S, B]"]) -> "StateT[S, B]":
        def new_run(state: S) -> Monad[tuple[B, S]]:
            return self.run(state).bind(
                lambda pair: f(pair[0]).run(pair[1])
            )
        return StateT(new_run)

    def __rshift__(self, f: Callable[[A], "StateT[S, B]"]) -> "StateT[S, B]":
        return self.bind(f)

    def __call__(self, state: S) -> Monad[tuple[A, S]]:
        return self.run(state)

    def __repr__(self) -> str:
        return f"StateT({self.run!r})"

    def __eq__(self, other: object) -> bool:
        """Structural equality for ``StateT`` is undefined.

        ``StateT`` wraps ``S -> m (a, S)`` functions. Comparing them directly
        would only check object identity.  Tests should compare the results of
        ``run`` for the same initial state instead.
        """
        return NotImplemented
