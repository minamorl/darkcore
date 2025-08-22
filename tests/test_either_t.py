from darkcore.either import Left, Right
from darkcore.either_t import EitherT

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
    et = EitherT.lift(m)
    assert isinstance(et, EitherT)
    assert et.run == DummyMonad(Right(10))


def test_map():
    m = DummyMonad(Right(3))
    et = EitherT(m)
    et2 = et.map(lambda x: x + 1)
    assert et2.run == DummyMonad(Right(4))


def test_bind_right():
    m = DummyMonad(Right(2))
    et = EitherT(m)

    def f(x):
        return EitherT(DummyMonad(Right(x * 10)))

    result = et.bind(f)
    assert result.run == DummyMonad(Right(20))


def test_bind_left():
    m = DummyMonad(Left("fail"))
    et = EitherT(m)

    def f(x):
        return EitherT(DummyMonad(Right(x * 10)))

    result = et.bind(f)
    assert result.run == DummyMonad(Left("fail"))


def test_ap():
    mf = DummyMonad(Right(lambda x: x + 5))
    mx = DummyMonad(Right(7))
    etf = EitherT(mf)
    etx = EitherT(mx)
    result = etf.ap(etx)
    assert result.run == DummyMonad(Right(12))
