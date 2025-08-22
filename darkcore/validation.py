from __future__ import annotations
from typing import Callable, Generic, List, TypeVar, Any, cast
from .core import MonadOpsMixin
from .result import Result, Ok, Err

E = TypeVar("E")
A = TypeVar("A")
B = TypeVar("B")

class Validation(MonadOpsMixin[A], Generic[E, A]):
    """Validation[E, A] = Success(A) | Failure(NonEmpty[List[E]]).

    Primarily an :class:`~darkcore.core.Applicative` that accumulates errors.
    ``bind`` propagates the first failure but does not accumulate errors from ``f``.
    """

    @classmethod
    def pure(cls, value: A) -> "Validation[E, A]":
        return Success(value)

    def fmap(self, f: Callable[[A], B]) -> "Validation[E, B]":  # pragma: no cover - interface
        raise NotImplementedError

    map = fmap

    def ap(self: "Validation[E, Callable[[A], B]]", fa: "Validation[E, A]") -> "Validation[E, B]":  # pragma: no cover - interface
        raise NotImplementedError

    def bind(self, f: Callable[[A], "Validation[E, B]"]) -> "Validation[E, B]":  # pragma: no cover - interface
        raise NotImplementedError

    def __rshift__(self, f: Callable[[A], "Validation[E, B]"]) -> "Validation[E, B]":
        raise NotImplementedError(
            "Validation is not a full Monad; use Result for short-circuiting"
        )


class Success(Validation[E, A]):
    __slots__ = ("value",)

    def __init__(self, value: A) -> None:
        self.value = value

    def fmap(self, f: Callable[[A], B]) -> "Validation[E, B]":
        return Success(f(self.value))

    def ap(self: "Success[E, Callable[[A], B]]", fa: "Validation[E, A]") -> "Validation[E, B]":
        if isinstance(fa, Success):
            func = self.value
            return Success(func(fa.value))
        return cast(Validation[E, B], fa)

    def bind(self, f: Callable[[A], "Validation[E, B]"]) -> "Validation[E, B]":
        return f(self.value)

    def __repr__(self) -> str:
        return f"Success({self.value!r})"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Success) and self.value == other.value


class Failure(Validation[E, Any]):
    __slots__ = ("errors",)

    def __init__(self, errors: List[E]) -> None:
        if not errors:
            raise ValueError("Failure requires a non-empty list of errors")
        self.errors = errors

    def fmap(self, f: Callable[[Any], B]) -> "Validation[E, B]":
        return cast(Validation[E, B], self)

    def ap(self, fa: "Validation[E, A]") -> "Validation[E, B]":
        if isinstance(fa, Failure):
            return Failure(self.errors + fa.errors)
        return cast(Validation[E, B], self)

    def bind(self, f: Callable[[Any], "Validation[E, B]"]) -> "Validation[E, B]":
        return cast(Validation[E, B], self)

    def __repr__(self) -> str:
        return f"Failure({self.errors!r})"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Failure) and self.errors == other.errors


def from_result(res: Result[A]) -> "Validation[str, A]":
    if isinstance(res, Ok):
        return Success(res.value)
    err = cast(Err[Any], res)
    return Failure([str(err.error)])


def to_result(val: Validation[E, A]) -> Result[A]:
    if isinstance(val, Success):
        return Ok(val.value)
    fail = cast(Failure[E], val)
    joined = ", ".join(str(e) for e in fail.errors)
    return Err(joined)
