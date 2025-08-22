from darkcore.result import Ok, Err
from darkcore.result_t import ResultT
from darkcore.result_t import ResultT
from darkcore.result import Ok, Err
import pytest


class DummyMonad:
    """Minimal monad for testing (only carries a value)."""
    def __init__(self, value):
        self.value = value

    @staticmethod
    def pure(x):
        return DummyMonad(x)

    def fmap(self, f):
        return DummyMonad(f(self.value))

    def bind(self, f):
        return f(self.value)

    def __eq__(self, other):
        return isinstance(other, DummyMonad) and self.value == other.value

    def __repr__(self):
        return f"DummyMonad({self.value!r})"


def test_lift():
    m = DummyMonad(10)
    rt = ResultT.lift(m)
    assert isinstance(rt, ResultT)
    assert rt.run == DummyMonad(Ok(10))


def test_map():
    m = DummyMonad(Ok(3))
    rt = ResultT(m)
    rt2 = rt.map(lambda x: x + 1)
    assert rt2.run == DummyMonad(Ok(4))


def test_bind_ok():
    m = DummyMonad(Ok(2))
    rt = ResultT(m)

    def f(x):
        return ResultT(DummyMonad(Ok(x * 10)))

    result = rt.bind(f)
    assert result.run == DummyMonad(Ok(20))


def test_bind_err():
    m = DummyMonad(Err("fail"))
    rt = ResultT(m)

    def f(x):
        return ResultT(DummyMonad(Ok(x * 10)))

    result = rt.bind(f)
    assert result.run == DummyMonad(Err("fail"))


def test_ap():
    mf = DummyMonad(Ok(lambda x: x + 5))
    mx = DummyMonad(Ok(7))
    rtf = ResultT(mf)
    rtx = ResultT(mx)
    result = rtf.ap(rtx)
    assert result.run == DummyMonad(Ok(12))


# Functor laws
@pytest.mark.parametrize("x", [1, 2])
def test_result_t_functor_identity(x):
    m = ResultT.lift(DummyMonad(x))
    assert m.fmap(lambda a: a) == m


def test_result_t_functor_composition():
    m = ResultT.lift(DummyMonad(3))
    f = lambda y: y + 1
    g = lambda y: y * 2
    assert m.fmap(lambda y: f(g(y))) == m.fmap(g).fmap(f)


# Applicative laws
def test_result_t_applicative_identity():
    v = ResultT.lift(DummyMonad(3))
    pure_id = ResultT.lift(DummyMonad(lambda x: x))
    assert pure_id.ap(v) == v


def test_result_t_applicative_homomorphism():
    f = lambda x: x + 1
    x = 3
    left = ResultT.lift(DummyMonad(f)).ap(ResultT.lift(DummyMonad(x)))
    right = ResultT.lift(DummyMonad(f(x)))
    assert left == right


def test_result_t_applicative_interchange():
    u = ResultT.lift(DummyMonad(lambda x: x * 2))
    y = 7
    left = u.ap(ResultT.lift(DummyMonad(y)))
    right = ResultT.lift(DummyMonad(lambda f: f(y))).ap(u)
    assert left == right


# Monad laws
def test_result_t_monad_left_identity():
    f = lambda x: ResultT.lift(DummyMonad(x + 1))
    x = 5
    assert ResultT.lift(DummyMonad(x)).bind(f) == f(x)


def test_result_t_monad_right_identity():
    m = ResultT.lift(DummyMonad(4))
    assert m.bind(lambda a: ResultT.lift(DummyMonad(a))) == m


def test_result_t_monad_associativity():
    m = ResultT.lift(DummyMonad(3))
    f = lambda x: ResultT.lift(DummyMonad(x + 1))
    g = lambda y: ResultT.lift(DummyMonad(y * 2))
    assert m.bind(f).bind(g) == m.bind(lambda x: f(x).bind(g))
