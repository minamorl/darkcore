from __future__ import annotations
from typing import Any, Callable, Generic, TypeVar, cast
from .core import Monad, MonadOpsMixin

R = TypeVar("R")
W = TypeVar("W")
S = TypeVar("S")
A = TypeVar("A")
B = TypeVar("B")

class RWST(MonadOpsMixin[A], Generic[R, W, S, A]):
    """Reader-Writer-State monad transformer."""

    def __init__(
        self,
        run: Callable[[R, S], Monad[tuple[tuple[A, S], W]]],
        *,
        combine: Callable[[W, W], W],
        empty: Callable[[], W],
    ) -> None:
        self.run = run
        self.combine = combine
        self.empty = empty

    @classmethod
    def pure_with(
        cls,
        pure: Callable[[tuple[tuple[A, S], W]], Monad[tuple[tuple[A, S], W]]],
        value: A,
        *,
        combine: Callable[[W, W], W],
        empty: Callable[[], W],
    ) -> "RWST[R, W, S, A]":
        return RWST(lambda _r, s: pure(((value, s), empty())), combine=combine, empty=empty)

    def fmap(self, f: Callable[[A], B]) -> "RWST[R, W, S, B]":
        def new_run(r: R, s: S) -> Monad[tuple[tuple[B, S], W]]:
            return self.run(r, s).fmap(lambda res: ((f(res[0][0]), res[0][1]), res[1]))
        return RWST(new_run, combine=self.combine, empty=self.empty)

    map = fmap

    def ap(
        self: "RWST[R, W, S, Callable[[A], B]]",
        fa: "RWST[R, W, S, A]",
    ) -> "RWST[R, W, S, B]":
        def new_run(r: R, s: S) -> Monad[tuple[tuple[B, S], W]]:
            m1 = self.run(r, s)
            return m1.bind(
                lambda pair_f: fa.run(r, pair_f[0][1]).bind(
                    lambda pair_a: cast(
                        Monad[tuple[tuple[B, S], W]],
                        cast(Any, m1).pure(
                            (
                                (pair_f[0][0](pair_a[0][0]), pair_a[0][1]),
                                self.combine(pair_f[1], pair_a[1]),
                            )
                        ),
                    )
                )
            )
        return RWST(new_run, combine=self.combine, empty=self.empty)

    def bind(self, f: Callable[[A], "RWST[R, W, S, B]"]) -> "RWST[R, W, S, B]":
        def new_run(r: R, s: S) -> Monad[tuple[tuple[B, S], W]]:
            m1 = self.run(r, s)
            return m1.bind(
                lambda pair: f(pair[0][0]).run(r, pair[0][1]).bind(
                    lambda res: cast(
                        Monad[tuple[tuple[B, S], W]],
                        cast(Any, m1).pure(
                            ((res[0][0], res[0][1]), self.combine(pair[1], res[1]))
                        ),
                    )
                )
            )
        return RWST(new_run, combine=self.combine, empty=self.empty)

    @classmethod
    def lift(
        cls,
        monad: Monad[A],
        *,
        combine: Callable[[W, W], W],
        empty: Callable[[], W],
    ) -> "RWST[R, W, S, A]":
        def run(r: R, s: S) -> Monad[tuple[tuple[A, S], W]]:
            def step(a: A) -> Monad[tuple[tuple[A, S], W]]:
                return cast(Monad[tuple[tuple[A, S], W]], cast(Any, monad).pure(((a, s), empty())))
            return monad.bind(step)
        return RWST(run, combine=combine, empty=empty)

    @classmethod
    def ask(
        cls,
        pure: Callable[[tuple[tuple[R, S], W]], Monad[tuple[tuple[R, S], W]]],
        *,
        combine: Callable[[W, W], W],
        empty: Callable[[], W],
    ) -> "RWST[R, W, S, R]":
        return RWST(lambda r, s: pure(((r, s), empty())), combine=combine, empty=empty)

    @classmethod
    def tell(
        cls,
        w: W,
        pure: Callable[[tuple[tuple[None, S], W]], Monad[tuple[tuple[None, S], W]]],
        *,
        combine: Callable[[W, W], W],
        empty: Callable[[], W],
    ) -> "RWST[R, W, S, None]":
        return RWST(lambda _r, s: pure(((None, s), w)), combine=combine, empty=empty)

    @classmethod
    def get(
        cls,
        pure: Callable[[tuple[tuple[S, S], W]], Monad[tuple[tuple[S, S], W]]],
        *,
        combine: Callable[[W, W], W],
        empty: Callable[[], W],
    ) -> "RWST[R, W, S, S]":
        return RWST(lambda _r, s: pure(((s, s), empty())), combine=combine, empty=empty)

    @classmethod
    def put(
        cls,
        new_state: S,
        pure: Callable[[tuple[tuple[None, S], W]], Monad[tuple[tuple[None, S], W]]],
        *,
        combine: Callable[[W, W], W],
        empty: Callable[[], W],
    ) -> "RWST[R, W, S, None]":
        return RWST(lambda _r, _s: pure(((None, new_state), empty())), combine=combine, empty=empty)

    @classmethod
    def modify(
        cls,
        f: Callable[[S], S],
        pure: Callable[[tuple[tuple[None, S], W]], Monad[tuple[tuple[None, S], W]]],
        *,
        combine: Callable[[W, W], W],
        empty: Callable[[], W],
    ) -> "RWST[R, W, S, None]":
        return RWST(lambda _r, s: pure(((None, f(s)), empty())), combine=combine, empty=empty)

    def __call__(self, r: R, s: S) -> Monad[tuple[tuple[A, S], W]]:
        return self.run(r, s)

    def __repr__(self) -> str:
        return f"RWST({self.run!r})"
