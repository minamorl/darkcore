from __future__ import annotations
from typing import Generic, TypeVar, Callable, Any, cast
from .core import Monad

A = TypeVar("A")
B = TypeVar("B")
W = TypeVar("W")  # ログ型（モノイド）


class WriterT(Generic[A, W]):
    """Writer モナドトランスフォーマー。``m (a, w)`` を包む。"""

    def __init__(self, run: Monad[tuple[A, W]], combine: Callable[[W, W], W] | None = None) -> None:
        self.run = run
        self.combine: Callable[[W, W], W] = combine or cast(Callable[[W, W], W], lambda a, b: a + b)

    @classmethod
    def lift(
        cls, monad: Monad[A], empty_log: W, *, combine: Callable[[W, W], W] | None = None
    ) -> "WriterT[A, W]":
        """m a -> WriterT m a"""
        combine_fn: Callable[[W, W], W] = combine or cast(Callable[[W, W], W], lambda a, b: a + b)

        def step(a: A) -> Monad[tuple[A, W]]:
            # 型変数不一致を回避するため Any/cast を用いる。
            return cast(Monad[tuple[A, W]], cast(Any, monad).pure((a, empty_log)))

        return WriterT(monad.bind(step), combine=combine_fn)

    @classmethod
    def pure_with(
        cls,
        pure: Callable[[tuple[A, W]], Monad[tuple[A, W]]],
        value: A,
        *,
        empty: Callable[[], W],
        combine: Callable[[W, W], W] | None = None,
    ) -> "WriterT[A, W]":
        """Construct ``WriterT`` with a supplied ``pure`` and ``empty`` (no HKTs)."""
        return WriterT(pure((value, empty())), combine=combine)

    def fmap(self, f: Callable[[A], B]) -> "WriterT[B, W]":
        return WriterT(self.run.fmap(lambda pair: (f(pair[0]), pair[1])), combine=self.combine)

    map = fmap

    def ap(self: "WriterT[Callable[[A], B], W]", fa: "WriterT[A, W]") -> "WriterT[B, W]":
        def step(pair_f: tuple[Callable[[A], B], W]) -> Monad[tuple[B, W]]:
            return fa.run.bind(
                lambda pair_a: cast(
                    Monad[tuple[B, W]],
                    cast(Any, self.run).pure(
                        (pair_f[0](pair_a[0]), self.combine(pair_f[1], pair_a[1]))
                    ),
                )
            )

        return WriterT(self.run.bind(step), combine=self.combine)

    def bind(self, f: Callable[[A], "WriterT[B, W]"]) -> "WriterT[B, W]":
        def step(pair: tuple[A, W]) -> Monad[tuple[B, W]]:
            (a, log1) = pair
            return f(a).run.bind(
                lambda res: cast(
                    Monad[tuple[B, W]],
                    cast(Any, self.run).pure((res[0], self.combine(log1, res[1]))),
                )
            )

        return WriterT(self.run.bind(step), combine=self.combine)

    def __rshift__(self, f: Callable[[A], "WriterT[B, W]"]) -> "WriterT[B, W]":
        return self.bind(f)

    def __repr__(self) -> str:
        return f"WriterT({self.run!r})"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, WriterT) and self.run == other.run
