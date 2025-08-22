from hypothesis import given, strategies as st, settings
from darkcore.maybe import Maybe
from darkcore.result import Ok, Err, Result
from darkcore.writer import Writer
from darkcore.validation import Success
from darkcore.rwst import RWST


small_int = st.integers(-5, 5)
small_str = st.text(min_size=0, max_size=5)
max_examples = settings(max_examples=25)


@max_examples
@given(small_int)
def test_functor_identity_maybe(x):
    m = Maybe(x)
    assert m.fmap(lambda a: a) == m


@max_examples
@given(small_int)
def test_functor_composition_maybe(x):
    m = Maybe(x)
    f = lambda a: a + 1
    g = lambda a: a * 2
    assert m.fmap(f).fmap(g) == m.fmap(lambda a: g(f(a)))


@max_examples
@given(small_int, small_int, small_int)
def test_applicative_composition_maybe(x, y, z):
    u = Maybe(lambda b: b + x)
    v = Maybe(lambda a: a * y)
    w = Maybe(z)
    compose = lambda f: lambda g: lambda a: f(g(a))
    left = Maybe(compose).ap(u).ap(v).ap(w)
    right = u.ap(v.ap(w))
    assert left == right


@max_examples
@given(small_int)
def test_monad_associativity_maybe(x):
    m = Maybe(x)
    f = lambda a: Maybe(a + 1)
    g = lambda a: Maybe(a * 2)
    assert m.bind(f).bind(g) == m.bind(lambda a: f(a).bind(g))


@max_examples
@given(small_int)
def test_functor_identity_result(x):
    r: Result[int] = Ok(x)
    assert r.fmap(lambda a: a) == r


@max_examples
@given(small_int)
def test_functor_composition_result(x):
    r: Result[int] = Ok(x)
    f = lambda a: a + 1
    g = lambda a: a * 2
    assert r.fmap(f).fmap(g) == r.fmap(lambda a: g(f(a)))


@max_examples
@given(small_int, small_int, small_int)
def test_applicative_composition_result(x, y, z):
    u: Result[callable] = Ok(lambda b: b + x)
    v: Result[callable] = Ok(lambda a: a * y)
    w: Result[int] = Ok(z)
    compose = lambda f: lambda g: lambda a: f(g(a))
    left = Ok(compose).ap(u).ap(v).ap(w)
    right = u.ap(v.ap(w))
    assert left == right


@max_examples
@given(small_int)
def test_monad_associativity_result(x):
    r: Result[int] = Ok(x)
    f = lambda a: Ok(a + 1)
    g = lambda a: Ok(a * 2)
    assert r.bind(f).bind(g) == r.bind(lambda a: f(a).bind(g))


@max_examples
@given(small_int)
def test_functor_identity_writer(x):
    w = Writer.pure(x)
    assert w.fmap(lambda a: a) == w


@max_examples
@given(small_int)
def test_functor_composition_writer(x):
    w = Writer.pure(x)
    f = lambda a: a + 1
    g = lambda a: a * 2
    assert w.fmap(f).fmap(g) == w.fmap(lambda a: g(f(a)))


@max_examples
@given(small_int, small_int, small_int)
def test_applicative_composition_writer(x, y, z):
    u = Writer.pure(lambda b: b + x)
    v = Writer.pure(lambda a: a * y)
    w = Writer.pure(z)
    compose = lambda f: lambda g: lambda a: f(g(a))
    left = Writer.pure(compose).ap(u).ap(v).ap(w)
    right = u.ap(v.ap(w))
    assert left == right


@max_examples
@given(small_int)
def test_monad_associativity_writer(x):
    w = Writer.pure(x)
    f = lambda a: Writer.pure(a + 1)
    g = lambda a: Writer.pure(a * 2)
    assert w.bind(f).bind(g) == w.bind(lambda a: f(a).bind(g))


@max_examples
@given(small_int)
def test_functor_identity_validation(x):
    v = Success(x)
    assert v.fmap(lambda a: a) == v


@max_examples
@given(small_int)
def test_functor_composition_validation(x):
    v = Success(x)
    f = lambda a: a + 1
    g = lambda a: a * 2
    assert v.fmap(f).fmap(g) == v.fmap(lambda a: g(f(a)))


@max_examples
@given(small_int, small_int, small_int)
def test_applicative_composition_validation(x, y, z):
    u = Success(lambda b: b + x)
    v = Success(lambda a: a * y)
    w = Success(z)
    compose = lambda f: lambda g: lambda a: f(g(a))
    left = Success(compose).ap(u).ap(v).ap(w)
    right = u.ap(v.ap(w))
    assert left == right


@max_examples
@given(small_int)
def test_functor_identity_rwst(x):
    pure = Ok.pure
    empty = list
    a = RWST.pure_with(pure, x, combine=lambda a, b: a + b, empty=empty)
    res1 = a.fmap(lambda y: y)(0, 0)
    res2 = a(0, 0)
    assert res1 == res2


@max_examples
@given(small_int)
def test_functor_composition_rwst(x):
    pure = Ok.pure
    empty = list
    a = RWST.pure_with(pure, x, combine=lambda a, b: a + b, empty=empty)
    f = lambda y: y + 1
    g = lambda y: y * 2
    res1 = a.fmap(f).fmap(g)(0, 0)
    res2 = a.fmap(lambda y: g(f(y)))(0, 0)
    assert res1 == res2


@max_examples
@given(small_int, small_int, small_int)
def test_applicative_composition_rwst(x, y, z):
    pure = Ok.pure
    empty = list
    u = RWST.pure_with(pure, lambda b: b + x, combine=lambda a, b: a + b, empty=empty)
    v = RWST.pure_with(pure, lambda a_: a_ * y, combine=lambda a, b: a + b, empty=empty)
    w = RWST.pure_with(pure, z, combine=lambda a, b: a + b, empty=empty)
    compose = lambda f: lambda g: lambda a_: f(g(a_))
    left = RWST.pure_with(pure, compose, combine=lambda a, b: a + b, empty=empty).ap(u).ap(v).ap(w)
    right = u.ap(v.ap(w))
    assert left(0, 0) == right(0, 0)


@max_examples
@given(small_int)
def test_monad_associativity_rwst(x):
    pure = Ok.pure
    empty = list
    a = RWST.pure_with(pure, x, combine=lambda a, b: a + b, empty=empty)
    f = lambda y: RWST.pure_with(pure, y + 1, combine=lambda a, b: a + b, empty=empty)
    g = lambda y: RWST.pure_with(pure, y * 2, combine=lambda a, b: a + b, empty=empty)
    res1 = a.bind(f).bind(g)(0, 0)
    res2 = a.bind(lambda y: f(y).bind(g))(0, 0)
    assert res1 == res2
