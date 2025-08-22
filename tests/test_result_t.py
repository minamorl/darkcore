from darkcore.result import Ok, Err
from darkcore.result_t import ResultT

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
