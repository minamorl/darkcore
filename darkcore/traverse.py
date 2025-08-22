from __future__ import annotations
from typing import Callable, List, Sequence, TypeVar, Any, cast
from .maybe import Maybe
from .result import Result, Ok, Err
from .core import SupportsFmapBindAp

A = TypeVar("A")
B = TypeVar("B")
T = TypeVar("T")
F = TypeVar("F", bound=SupportsFmapBindAp[Any])

def sequence_maybe(xs: Sequence[Maybe[A]]) -> Maybe[List[A]]:
    acc: Maybe[List[A]] = Maybe.pure(cast(List[A], []))
    for m in xs:
        acc = liftA2(lambda lst, v: lst + [v], acc, m)
    return acc

def traverse_maybe(xs: Sequence[T], f: Callable[[T], Maybe[A]]) -> Maybe[List[A]]:
    return sequence_maybe([f(x) for x in xs])

def sequence_result(xs: Sequence[Result[A]]) -> Result[List[A]]:
    acc: List[A] = []
    for r in xs:
        if isinstance(r, Err):
            return cast(Result[List[A]], r)
        acc.append(cast(Ok[A], r).value)
    return Ok(acc)

def traverse_result(xs: Sequence[T], f: Callable[[T], Result[A]]) -> Result[List[A]]:
    return sequence_result([f(x) for x in xs])

def liftA2(
    f: Callable[[A, B], T], fa: SupportsFmapBindAp[A], fb: SupportsFmapBindAp[B]
) -> Any:
    return fa.fmap(lambda a: (lambda b: f(a, b))).ap(fb)

def left_then(fa: SupportsFmapBindAp[A], fb: SupportsFmapBindAp[B]) -> Any:
    return liftA2(lambda a, _b: a, fa, fb)

def then_right(fa: SupportsFmapBindAp[A], fb: SupportsFmapBindAp[B]) -> Any:
    return liftA2(lambda _a, b: b, fa, fb)
