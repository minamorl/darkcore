from darkcore.maybe import Maybe
from darkcore.maybe_t import MaybeT
import pytest

class DummyMonad:
    """テスト用の最小Monad実装（Just値しか持たない）"""
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
        if not isinstance(other, DummyMonad):
            return False
        return self.value == other.value

    def __repr__(self):
        return f"DummyMonad({self.value!r})"


def test_lift():
    m = DummyMonad(10)
    mt = MaybeT.lift(m)
    assert isinstance(mt, MaybeT)
    assert mt.run == DummyMonad(Maybe(10))

def test_map():
    m = DummyMonad(Maybe(3))
    mt = MaybeT(m)
    mt2 = mt.map(lambda x: x + 1)
    assert mt2.run == DummyMonad(Maybe(4))

def test_bind_success():
    m = DummyMonad(Maybe(2))
    mt = MaybeT(m)

    def f(x):
        return MaybeT(DummyMonad(Maybe(x * 10)))

    result = mt.bind(f)
    assert result.run == DummyMonad(Maybe(20))

def test_bind_nothing():
    m = DummyMonad(Maybe(None))
    mt = MaybeT(m)

    def f(x):
        return MaybeT(DummyMonad(Maybe(x * 10)))

    result = mt.bind(f)
    assert result.run == DummyMonad(Maybe(None))

def test_ap():
    mf = DummyMonad(Maybe(lambda x: x + 5))
    mx = DummyMonad(Maybe(7))

    mtf = MaybeT(mf)
    mtx = MaybeT(mx)

    result = mtf.ap(mtx)
    assert result.run == DummyMonad(Maybe(12))


# Functor laws
@pytest.mark.parametrize("x", [1, 2])
def test_maybe_t_functor_identity(x):
    m = MaybeT.lift(DummyMonad(x))
    assert m.fmap(lambda a: a) == m


@pytest.mark.parametrize("x", [3])
def test_maybe_t_functor_composition(x):
    m = MaybeT.lift(DummyMonad(x))
    f = lambda y: y + 1
    g = lambda y: y * 2
    assert m.fmap(lambda y: f(g(y))) == m.fmap(g).fmap(f)


# Applicative laws
def test_maybe_t_applicative_identity():
    v = MaybeT.lift(DummyMonad(3))
    pure_id = MaybeT.lift(DummyMonad(lambda x: x))
    assert pure_id.ap(v) == v


def test_maybe_t_applicative_homomorphism():
    f = lambda x: x + 1
    x = 3
    left = MaybeT.lift(DummyMonad(f)).ap(MaybeT.lift(DummyMonad(x)))
    right = MaybeT.lift(DummyMonad(f(x)))
    assert left == right


def test_maybe_t_applicative_interchange():
    u = MaybeT.lift(DummyMonad(lambda x: x * 2))
    y = 7
    left = u.ap(MaybeT.lift(DummyMonad(y)))
    right = MaybeT.lift(DummyMonad(lambda f: f(y))).ap(u)
    assert left == right


# Monad laws
def test_maybe_t_monad_left_identity():
    f = lambda x: MaybeT.lift(DummyMonad(x + 1))
    x = 5
    assert MaybeT.lift(DummyMonad(x)).bind(f) == f(x)


def test_maybe_t_monad_right_identity():
    m = MaybeT.lift(DummyMonad(4))
    assert m.bind(lambda a: MaybeT.lift(DummyMonad(a))) == m


def test_maybe_t_monad_associativity():
    m = MaybeT.lift(DummyMonad(3))
    f = lambda x: MaybeT.lift(DummyMonad(x + 1))
    g = lambda y: MaybeT.lift(DummyMonad(y * 2))
    assert m.bind(f).bind(g) == m.bind(lambda x: f(x).bind(g))
