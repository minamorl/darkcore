from darkcore.validation import Success, Failure
from darkcore.validation_t import ValidationT
from darkcore.result import Ok


def test_functor_identity():
    vt = ValidationT(Ok(Success(1)))
    assert vt.fmap(lambda x: x).run == Ok(Success(1))


def test_functor_composition():
    vt = ValidationT(Ok(Success(2)))
    f = lambda x: x + 1
    g = lambda x: x * 2
    left = vt.fmap(f).fmap(g).run
    right = vt.fmap(lambda x: g(f(x))).run
    assert left == right


def test_applicative_identity():
    v = ValidationT(Ok(Success(3)))
    identity = ValidationT(Ok(Success(lambda x: x)))
    assert identity.ap(v).run == Ok(Success(3))


def test_applicative_homomorphism():
    f = lambda x: x + 5
    x = 3
    left = ValidationT(Ok(Success(f))).ap(ValidationT(Ok(Success(x)))).run
    right = Ok(Success(f(x)))
    assert left == right


def test_applicative_interchange():
    u = ValidationT(Ok(Success(lambda x: x + 1)))
    y = 2
    left = u.ap(ValidationT(Ok(Success(y)))).run
    right = ValidationT(Ok(Success(lambda g: g(y)))).ap(u).run
    assert left == right


def test_applicative_composition():
    u = ValidationT(Ok(Success(lambda y: y * 2)))
    v = ValidationT(Ok(Success(lambda x: x + 3)))
    w = ValidationT(Ok(Success(1)))
    compose = lambda f: lambda g: lambda x: f(g(x))
    left = ValidationT(Ok(Success(compose))).ap(u).ap(v).ap(w).run
    right = u.ap(v.ap(w)).run
    assert left == right


def test_failure_accumulates():
    f1 = ValidationT(Ok(Failure(["e1"])))
    f2 = ValidationT(Ok(Failure(["e2"])))
    res = f1.ap(f2).run
    assert res == Ok(Failure(["e1", "e2"]))


def test_lift_and_bind_failure():
    vt = ValidationT.lift(Ok(1))
    assert vt.run == Ok(Success(1))
    fail = ValidationT(Ok(Failure(["e"])))
    res = fail.bind(lambda x: ValidationT(Ok(Success(x + 1)))).run
    assert res == Ok(Failure(["e"]))
