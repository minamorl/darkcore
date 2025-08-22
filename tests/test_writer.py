from darkcore.writer import Writer
from darkcore.writer import Writer
import pytest


def test_writer_bind_and_tell():
    w = Writer.pure(3).tell(["start"]) >> (lambda x: Writer(x + 1, ["inc"]))
    assert w.value == 4
    assert w.log == ["start", "inc"]


def test_writer_fmap():
    w = Writer(5, ["init"]) | (lambda x: x * 2)
    assert w == Writer(10, ["init"])


def test_writer_ap_and_operator():
    wf = Writer(lambda x: x + 1, ["f"])
    wx = Writer(2, ["x"])
    res = wf @ wx
    assert res == Writer(3, ["f", "x"])


# Functor laws
def test_writer_functor_identity():
    w = Writer(3, ["log"])
    assert (w | (lambda x: x)) == w


def test_writer_functor_composition():
    w = Writer(2, ["log"])
    f = lambda x: x + 3
    g = lambda x: x * 4
    assert (w | (lambda x: f(g(x)))) == ((w | g) | f)


# Applicative laws
def test_writer_applicative_identity():
    v = Writer(5, ["v"])
    assert (Writer.pure(lambda x: x) @ v) == v


def test_writer_applicative_homomorphism():
    f = lambda x: x + 1
    x = 3
    left = Writer.pure(f) @ Writer.pure(x)
    right = Writer.pure(f(x))
    assert left == right


def test_writer_applicative_interchange():
    u = Writer.pure(lambda x: x * 2)
    y = 7
    left = u @ Writer.pure(y)
    right = Writer.pure(lambda f: f(y)) @ u
    assert left == right


# Monad laws
def test_writer_monad_left_identity():
    f = lambda x: Writer(x + 1, ["f"])
    x = 5
    assert Writer.pure(x).bind(f) == f(x)


def test_writer_monad_right_identity():
    m = Writer(4, ["m"])
    assert m.bind(Writer.pure) == m


def test_writer_monad_associativity():
    m = Writer(1, ["m"])
    f = lambda x: Writer(x + 1, ["f"])
    g = lambda y: Writer(y * 2, ["g"])
    assert m.bind(f).bind(g) == m.bind(lambda x: f(x).bind(g))
