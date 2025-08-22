from darkcore.reader import Reader
import pytest


def test_reader_basic():
    r = Reader(lambda env: env + 1)
    assert r.run(10) == 11


def test_reader_map_operator():
    r = Reader(lambda env: env) | (lambda x: x + 1)
    assert r.run(2) == 3


def test_reader_bind():
    r = Reader(lambda env: env * 2)
    s = r >> (lambda x: Reader(lambda env: x + env))
    # env=3 のとき: r=6, その後 f(6) = Reader(lambda env: 6+env)=9
    assert s.run(3) == 9


def test_reader_ap_operator():
    rf = Reader(lambda env: lambda x: x + env)
    rx = Reader(lambda env: env * 2)
    r = rf @ rx
    assert r.run(3) == 9


# Functor laws
@pytest.mark.parametrize("env", [0, 1, 5])
def test_reader_functor_identity(env):
    r = Reader(lambda e: e + 1)
    assert (r | (lambda x: x)).run(env) == r.run(env)


@pytest.mark.parametrize("env", [0, 2])
def test_reader_functor_composition(env):
    r = Reader(lambda e: e * 2)
    f = lambda x: x + 3
    g = lambda x: x * 4
    lhs = r | (lambda x: f(g(x)))
    rhs = (r | g) | f
    assert lhs.run(env) == rhs.run(env)


# Applicative laws
@pytest.mark.parametrize("env", [1, 3])
def test_reader_applicative_identity(env):
    v = Reader(lambda e: e + 5)
    assert (Reader.pure(lambda x: x) @ v).run(env) == v.run(env)


@pytest.mark.parametrize("env", [0])
def test_reader_applicative_homomorphism(env):
    f = lambda x: x + 1
    x = 3
    left = Reader.pure(f) @ Reader.pure(x)
    right = Reader.pure(f(x))
    assert left.run(env) == right.run(env)


@pytest.mark.parametrize("env", [2])
def test_reader_applicative_interchange(env):
    u = Reader.pure(lambda x: x * 2)
    y = 7
    left = u @ Reader.pure(y)
    right = Reader.pure(lambda f: f(y)) @ u
    assert left.run(env) == right.run(env)


# Monad laws
@pytest.mark.parametrize("env", [0, 4])
def test_reader_monad_left_identity(env):
    f = lambda x: Reader(lambda r: x + r)
    x = 5
    assert Reader.pure(x).bind(f).run(env) == f(x).run(env)


@pytest.mark.parametrize("env", [1, 2])
def test_reader_monad_right_identity(env):
    m = Reader(lambda r: r * 2)
    assert m.bind(Reader.pure).run(env) == m.run(env)


@pytest.mark.parametrize("env", [3])
def test_reader_monad_associativity(env):
    m = Reader(lambda r: r + 1)
    f = lambda x: Reader(lambda r: x * r)
    g = lambda y: Reader(lambda r: y - r)
    left = m.bind(f).bind(g)
    right = m.bind(lambda x: f(x).bind(g))
    assert left.run(env) == right.run(env)
