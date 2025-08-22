from __future__ import annotations
from typing import Callable, Generic, TypeVar, Any, cast
from .core import Monad as MonadLike
from .validation import Validation, Success, Failure

E = TypeVar("E")
A = TypeVar("A")
B = TypeVar("B")

class ValidationT(Generic[E, A]):
    """Monad transformer for :class:`~darkcore.validation.Validation`.

    Wraps ``m (Validation e a)``.
    """

    def __init__(self, run: MonadLike[Validation[E, A]]) -> None:
        self.run = run

    @classmethod
    def lift(cls, monad: MonadLike[A]) -> "ValidationT[E, A]":
        def step(x: A) -> MonadLike[Validation[E, A]]:
            return cast(MonadLike[Validation[E, A]], cast(Any, monad).pure(Success(x)))
        return ValidationT(cast(MonadLike[Validation[E, A]], monad.bind(step)))

    def fmap(self, f: Callable[[A], B]) -> "ValidationT[E, B]":
        def step(val: Validation[E, A]) -> MonadLike[Validation[E, B]]:
            return cast(
                MonadLike[Validation[E, B]],
                cast(Any, self.run).pure(val.fmap(f)),
            )
        return ValidationT(self.run.bind(step))

    map = fmap

    def ap(self: "ValidationT[E, Callable[[A], B]]", fa: "ValidationT[E, A]") -> "ValidationT[E, B]":
        return ValidationT(
            self.run.bind(
                lambda mf: fa.run.bind(
                    lambda mx: cast(
                        MonadLike[Validation[E, B]],
                        cast(Any, self.run).pure(cast(Any, mf).ap(mx)),
                    )
                )
            )
        )

    def bind(self, f: Callable[[A], "ValidationT[E, B]"]) -> "ValidationT[E, B]":
        def step(val: Validation[E, A]) -> MonadLike[Validation[E, B]]:
            if isinstance(val, Failure):
                return cast(MonadLike[Validation[E, B]], cast(Any, self.run).pure(val))
            succ = cast(Success[E, A], val)
            return f(succ.value).run
        return ValidationT(self.run.bind(step))

    def __eq__(self, other: object) -> bool:  # pragma: no cover - structural
        return isinstance(other, ValidationT) and self.run == other.run

    def __repr__(self) -> str:  # pragma: no cover - debug
        return f"ValidationT({self.run!r})"
