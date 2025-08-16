from __future__ import annotations
from typing import Generic, TypeVar, List, Callable, Any, cast
from .core import Monad

A = TypeVar("A")
B = TypeVar("B")
W = TypeVar("W")  # ログ型（モノイド想定：ここでは List[W] を連結）

class WriterT(Generic[A, W]):
    """
    WriterT m a ≅ m (a, w)
    ここで w はモノイド（リスト連結で代用）。
    """
    def __init__(self, run: Monad[tuple[A, List[W]]]) -> None:
        self.run = run

    @classmethod
    def lift(cls, monad: Monad[A], empty_log: List[W]) -> "WriterT[A, W]":
        """
        m a -> WriterT m a
        実装上は: monad.bind(lambda a: monad.pure((a, empty_log)))
        ただし mypy の型変数不一致を回避するため cast を用いる。
        """
        def step(a: A) -> Monad[tuple[A, List[W]]]:
            # monad.pure は A に限らず「そのモナドの型パラメタ全体」に対して多相だが、
            # Python の型システムでは単相に見えるため Any/cast で橋渡しする。
            return cast(Monad[tuple[A, List[W]]],
                        cast(Any, monad).pure((a, empty_log)))
        return WriterT(monad.bind(step))

    def bind(self, f: Callable[[A], "WriterT[B, W]"]) -> "WriterT[B, W]":
        """
        (a, w1) を取り出し、f(a) の run = m (b, w2) を連鎖。
        ログは w1 ++ w2（ここではリスト結合）。
        """
        def step(pair: tuple[A, List[W]]) -> Monad[tuple[B, List[W]]]:
            (a, log1) = pair
            # f(a).run: Monad[(B, List[W])]
            return f(a).run.bind(
                lambda res: cast(Monad[tuple[B, List[W]]],
                                 cast(Any, self.run).pure((res[0], log1 + res[1])))
            )

        return WriterT(self.run.bind(step))

    def __rshift__(self, f: Callable[[A], "WriterT[B, W]"]) -> "WriterT[B, W]":
        return self.bind(f)

    def __repr__(self) -> str:
        return f"WriterT({self.run!r})"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, WriterT) and self.run == other.run
