from darkcore.maybe import Maybe
from darkcore.maybe_t import MaybeT

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
