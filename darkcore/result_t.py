from __future__ import annotations
from typing import Callable, Generic, TypeVar, Any
from .core import Monad as MonadLike
from .result import Result, Ok, Err

A = TypeVar("A")
B = TypeVar("B")

class ResultT(Generic[A]):
    """Monad transformer for Result.

    Wraps: m (Result a)
    """

    def __init__(self, run: MonadLike[Any]) -> None:
        self.run: MonadLike[Any] = run

    @classmethod
    def lift(cls, monad: MonadLike[A]) -> "ResultT[A]":
        """Lift a monad into ResultT."""
        return ResultT(monad.bind(lambda x: monad.pure(Ok(x))))  # type: ignore[arg-type]

    def map(self, f: Callable[[A], B]) -> "ResultT[B]":
        return ResultT(self.run.bind(lambda r: self.run.pure(r.fmap(f))))

    def ap(self: "ResultT[Callable[[A], B]]", fa: "ResultT[A]") -> "ResultT[B]":
        return ResultT(self.run.bind(lambda mf: fa.run.bind(lambda mx: self.run.pure(mf.ap(mx)))))

    def bind(self, f: Callable[[A], "ResultT[B]"]) -> "ResultT[B]":
        def step(result: Result[A]) -> MonadLike[Any]:
            if isinstance(result, Err):
                return self.run.pure(result)
            else:
                return f(result.value).run
        return ResultT(self.run.bind(step))

    def __eq__(self, other: object) -> bool:
        return isinstance(other, ResultT) and self.run == other.run

    def __repr__(self) -> str:
        return f"ResultT({self.run!r})"
