from __future__ import annotations
from typing import Callable, Generic, TypeVar, Any, cast
from .core import Monad as MonadLike
from .result import Result, Ok, Err

A = TypeVar("A")
B = TypeVar("B")

class ResultT(Generic[A]):
    """Monad transformer for :class:`~darkcore.result.Result`.

    Wraps ``m (Result a)``.
    """

    def __init__(self, run: MonadLike[Result[A]]) -> None:
        self.run = run

    @classmethod
    def lift(cls, monad: MonadLike[A]) -> "ResultT[A]":
        def step(x: A) -> MonadLike[Result[A]]:
            return cast(MonadLike[Result[A]], cast(Any, monad).pure(Ok(x)))
        return ResultT(cast(MonadLike[Result[A]], monad.bind(step)))

    def fmap(self, f: Callable[[A], B]) -> "ResultT[B]":
        def step(res: Result[A]) -> MonadLike[Result[B]]:
            if isinstance(res, Err):
                return cast(MonadLike[Result[B]], self.run.pure(res))
            ok = cast(Ok[A], res)
            return cast(
                MonadLike[Result[B]],
                cast(Any, self.run).pure(cast(Result[B], Ok(f(ok.value))))
            )

        return ResultT(self.run.bind(step))

    map = fmap

    def ap(self: "ResultT[Callable[[A], B]]", fa: "ResultT[A]") -> "ResultT[B]":
        return ResultT(
            self.run.bind(
                lambda mf: fa.run.bind(
                    lambda mx: cast(MonadLike[Result[B]], self.run.pure(mf.ap(mx)))
                )
            )
        )

    def bind(self, f: Callable[[A], "ResultT[B]"]) -> "ResultT[B]":
        def step(res: Result[A]) -> MonadLike[Result[B]]:
            if isinstance(res, Err):
                return cast(MonadLike[Result[B]], self.run.pure(res))
            ok = cast(Ok[A], res)
            return f(ok.value).run
        return ResultT(self.run.bind(step))

    def __eq__(self, other: object) -> bool:
        return isinstance(other, ResultT) and self.run == other.run

    def __repr__(self) -> str:
        return f"ResultT({self.run!r})"
