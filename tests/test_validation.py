import pytest
from darkcore.validation import Success, Failure, from_result, to_result
from darkcore.result import Ok, Err


def test_fmap_identity():
    assert Success(1).fmap(lambda x: x) == Success(1)
    assert Failure(["e"]).fmap(lambda x: x) == Failure(["e"])


def test_fmap_composition():
    f = lambda x: x + 1
    g = lambda x: x * 2
    v = Success(3)
    assert v.fmap(f).fmap(g) == v.fmap(lambda x: g(f(x)))


def test_applicative_identity():
    v = Success(10)
    assert Success(lambda x: x).ap(v) == v


def test_applicative_homomorphism():
    f = lambda x: x + 5
    x = 3
    assert Success(f).ap(Success(x)) == Success(f(x))


def test_applicative_interchange():
    f = Success(lambda x: x + 1)
    y = 2
    assert f.ap(Success(y)) == Success(lambda g: g(y)).ap(f)


def test_applicative_composition():
    u = Success(lambda y: y * 2)
    v = Success(lambda x: x + 3)
    w = Success(1)
    compose = lambda f: lambda g: lambda x: f(g(x))
    left = Success(compose).ap(u).ap(v).ap(w)
    right = u.ap(v.ap(w))
    assert left == right


def test_failure_accumulates():
    f1 = Failure(["e1"])
    f2 = Failure(["e2"])
    assert f1.ap(Success(1)) == f1
    assert Success(lambda x: x).ap(f1) == f1
    assert f1.ap(f2) == Failure(["e1", "e2"])


def test_from_to_result_roundtrip():
    ok = Ok(1)
    err = Err("x")
    assert from_result(ok) == Success(1)
    assert from_result(err) == Failure(["x"])
    assert to_result(Success(2)) == Ok(2)
    assert to_result(Failure(["a", "b"])) == Err("a, b")


def test_non_commutative_errors():
    e1 = ("tag1", "a")
    e2 = ("tag2", "b")
    f1 = Failure([e1])
    f2 = Failure([e2])
    assert f1.ap(f2) == Failure([e1, e2])
