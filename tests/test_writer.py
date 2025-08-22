# tests for Writer
import pytest
from darkcore.writer import Writer


def writer_list(value, log=None):
    return Writer(value, log if log is not None else [])


def writer_str(value, log=None):
    return Writer(value, log if log is not None else "", combine=str.__add__, empty=str)


def test_writer_requires_explicit_monoid():
    with pytest.raises(TypeError):
        Writer(1, "")

# Functor laws
@pytest.mark.parametrize("factory,log", [
    (writer_list, ["log"]),
    (writer_str, "log"),
])
def test_writer_functor_identity(factory, log):
    w = factory(3, log)
    assert (w | (lambda x: x)) == w


@pytest.mark.parametrize("factory,log", [
    (writer_list, ["log"]),
    (writer_str, "log"),
])
def test_writer_functor_composition(factory, log):
    w = factory(2, log)
    f = lambda x: x + 3
    g = lambda x: x * 4
    assert (w | (lambda x: f(g(x)))) == ((w | g) | f)

# Applicative laws
@pytest.mark.parametrize("factory,log", [
    (writer_list, ["v"]),
    (writer_str, "v"),
])
def test_writer_applicative_identity(factory, log):
    v = factory(5, log)
    pure_id = factory(lambda x: x)
    assert (pure_id @ v) == v


@pytest.mark.parametrize("factory", [writer_list, writer_str])
def test_writer_applicative_homomorphism(factory):
    f = lambda x: x + 1
    x = 3
    left = factory(f) @ factory(x)
    right = factory(f(x))
    assert left == right


@pytest.mark.parametrize("factory", [writer_list, writer_str])
def test_writer_applicative_interchange(factory):
    u = factory(lambda x: x * 2)
    y = 7
    left = u @ factory(y)
    right = factory(lambda f: f(y)) @ u
    assert left == right


@pytest.mark.parametrize("factory", [writer_list, writer_str])
def test_writer_applicative_composition(factory):
    compose = lambda f: lambda g: lambda x: f(g(x))
    u = factory(lambda x: x + 1)
    v = factory(lambda x: x * 2)
    w = factory(3)
    left = factory(compose) @ u @ v @ w
    right = u @ (v @ w)
    assert left == right

# Monad laws
@pytest.mark.parametrize("factory", [writer_list, writer_str])
def test_writer_monad_left_identity(factory):
    f = lambda x: factory(x + 1)
    x = 5
    assert factory(x).bind(f) == f(x)


@pytest.mark.parametrize("factory,log", [
    (writer_list, ["m"]),
    (writer_str, "m"),
])
def test_writer_monad_right_identity(factory, log):
    m = factory(4, log)
    assert m.bind(factory) == m


@pytest.mark.parametrize("factory", [writer_list, writer_str])
def test_writer_monad_associativity(factory):
    m = factory(1)
    f = lambda x: factory(x + 1)
    g = lambda y: factory(y * 2)
    assert m.bind(f).bind(g) == m.bind(lambda x: f(x).bind(g))
