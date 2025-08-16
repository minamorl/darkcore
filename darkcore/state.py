from __future__ import annotations
from typing import Callable, Generic, TypeVar, Tuple

S = TypeVar("S")  # State
A = TypeVar("A")
B = TypeVar("B")

class State(Generic[S, A]):
    def __init__(self, run: Callable[[S], Tuple[A, S]]) -> None:
        self.run = run

    @classmethod
    def pure(cls, value: A) -> State[S, A]:
        return State(lambda s: (value, s))

    def fmap(self, f: Callable[[A], B]) -> State[S, B]:
        def new_run(s: S) -> Tuple[B, S]:
            (a, s1) = self.run(s)
            return (f(a), s1)
        return State(new_run)

    def bind(self, f: Callable[[A], State[S, B]]) -> State[S, B]:
        def new_run(s: S) -> Tuple[B, S]:
            (a, s1) = self.run(s)
            return f(a).run(s1)
        return State(new_run)

    @staticmethod
    def get() -> State[S, S]:
        return State(lambda s: (s, s))

    @staticmethod
    def put(new_state: S) -> State[S, None]:
        return State(lambda _: (None, new_state))

    def __repr__(self) -> str:
        return f"State({self.run})"
