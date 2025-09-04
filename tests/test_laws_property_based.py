from __future__ import annotations

from hypothesis import given, strategies as st

from darkcore.maybe import Maybe
from darkcore.result import Ok
from darkcore.validation import Success


@given(st.integers())
def test_functor_identity_maybe(x: int) -> None:
    m = Maybe(x)
    assert (m | (lambda v: v)) == m


@given(st.integers())
def test_monad_associativity_result(x: int) -> None:
    r = Ok(x)
    f = lambda a: Ok(a + 1)
    g = lambda a: Ok(a * 2)
    assert ((r >> f) >> g) == (r >> (lambda a: f(a) >> g))


@given(st.integers(), st.integers(), st.integers())
def test_applicative_composition_validation(x: int, y: int, z: int) -> None:
    u = Success(lambda b: b + x)
    v = Success(lambda a: a * y)
    w = Success(z)
    compose = lambda f: lambda g: lambda a: f(g(a))
    left = Success(compose) @ u @ v @ w
    right = u @ (v @ w)
    assert left == right
