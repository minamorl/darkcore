import pytest
from darkcore.writer_t import WriterT
from darkcore.result import Ok, Err


def wt_list(value, log=None):
    return WriterT(Ok((value, log if log is not None else [])))


def wt_str(value, log=None):
    return WriterT(Ok((value, log if log is not None else "")), combine=str.__add__)


def test_writer_t_lift_and_run():
    wt = WriterT.lift(Ok(42), [])
    assert wt.run == Ok((42, []))


def test_writer_t_err_propagates():
    wt = WriterT(Err("fail"))
    def step(x: int) -> WriterT[int, int]:
        return WriterT(Ok((x*2, ["doubled"])))
    res = wt >> step
    assert res.run == Err("fail")

# Functor laws
@pytest.mark.parametrize("factory,log", [
    (wt_list, ["log"]),
    (wt_str, "log"),
])
def test_writer_t_functor_identity(factory, log):
    w = factory(3, log)
    assert w.fmap(lambda a: a).run == w.run


@pytest.mark.parametrize("factory,log", [
    (wt_list, ["log"]),
    (wt_str, "log"),
])
def test_writer_t_functor_composition(factory, log):
    w = factory(2, log)
    f = lambda x: x + 1
    g = lambda x: x * 2
    assert w.fmap(lambda x: f(g(x))).run == w.fmap(g).fmap(f).run

# Applicative laws
@pytest.mark.parametrize("factory,log", [
    (wt_list, ["v"]),
    (wt_str, "v"),
])
def test_writer_t_applicative_identity(factory, log):
    v = factory(5, log)
    pure_id = factory(lambda x: x)
    assert pure_id.ap(v).run == v.run


@pytest.mark.parametrize("factory,log", [
    (wt_list, None),
    (wt_str, None),
])
def test_writer_t_applicative_homomorphism(factory, log):
    f = lambda x: x + 1
    x = 3
    left = factory(f).ap(factory(x))
    right = factory(f(x))
    assert left.run == right.run


@pytest.mark.parametrize("factory,log", [
    (wt_list, None),
    (wt_str, None),
])
def test_writer_t_applicative_interchange(factory, log):
    u = factory(lambda x: x * 2)
    y = 7
    left = u.ap(factory(y))
    right = factory(lambda f: f(y)).ap(u)
    assert left.run == right.run

# Monad laws
@pytest.mark.parametrize("factory,log", [
    (wt_list, None),
    (wt_str, None),
])
def test_writer_t_monad_left_identity(factory, log):
    f = lambda x: factory(x + 1)
    x = 5
    assert factory(x).bind(f).run == f(x).run


@pytest.mark.parametrize("factory,log", [
    (wt_list, ["m"]),
    (wt_str, "m"),
])
def test_writer_t_monad_right_identity(factory, log):
    m = factory(4, log)
    assert m.bind(lambda a: factory(a)).run == m.run


@pytest.mark.parametrize("factory,log", [
    (wt_list, None),
    (wt_str, None),
])
def test_writer_t_monad_associativity(factory, log):
    m = factory(1)
    f = lambda x: factory(x + 1)
    g = lambda y: factory(y * 2)
    left = m.bind(f).bind(g).run
    right = m.bind(lambda x: f(x).bind(g)).run
    assert left == right
