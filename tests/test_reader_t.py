from darkcore.result import Ok, Err
from darkcore.reader_t import ReaderT
from darkcore.result import Ok
import pytest

def test_reader_t_lift():
    rt = ReaderT.lift(Ok(42))
    assert rt.run({"env": "dummy"}) == Ok(42)

def test_reader_t_basic_bind():
    # ReaderT returning threshold from env
    prog = ReaderT(lambda env: Ok(env["threshold"])) >> (
        lambda t: ReaderT(lambda env: Ok(t * 2))
    )

    res = prog.run({"threshold": 10})
    assert res == Ok(20)

def test_reader_t_err_propagates():
    prog = ReaderT(lambda env: Err("missing")) >> (
        lambda t: ReaderT(lambda env: Ok(t * 2))
    )

    res = prog.run({"threshold": 10})
    assert res == Err("missing")

def test_reader_t_composition():
    def step1(x: int) -> ReaderT[dict, int]:
        return ReaderT(lambda env: Ok(x + env.get("bonus", 0)))

    def step2(x: int) -> ReaderT[dict, str]:
        return ReaderT(lambda env: Ok(f"user={env['user']}, val={x}"))

    prog = ReaderT(lambda env: Ok(env["base"])) >> step1 >> step2

    res = prog.run({"base": 5, "bonus": 3, "user": "alice"})
    assert res == Ok("user=alice, val=8")


# Functor laws
@pytest.mark.parametrize("env", [{"x": 1}, {"x": 2}])
def test_reader_t_functor_identity(env):
    r = ReaderT(lambda e: Ok(e["x"]))
    assert r.fmap(lambda a: a).run(env) == r.run(env)


@pytest.mark.parametrize("env", [{"x": 3}])
def test_reader_t_functor_composition(env):
    r = ReaderT(lambda e: Ok(e["x"]))
    f = lambda y: y + 1
    g = lambda y: y * 2
    lhs = r.fmap(lambda y: f(g(y)))
    rhs = r.fmap(g).fmap(f)
    assert lhs.run(env) == rhs.run(env)


# Applicative laws
@pytest.mark.parametrize("env", [{"x": 5}])
def test_reader_t_applicative_identity(env):
    v = ReaderT(lambda e: Ok(e["x"]))
    pure_id = ReaderT(lambda _: Ok(lambda x: x))
    assert pure_id.ap(v).run(env) == v.run(env)


def test_reader_t_applicative_homomorphism():
    f = lambda x: x + 1
    x = 3
    left = ReaderT(lambda _: Ok(f)).ap(ReaderT(lambda _: Ok(x)))
    right = ReaderT(lambda _: Ok(f(x)))
    assert left.run({}) == right.run({})


def test_reader_t_applicative_interchange():
    u = ReaderT(lambda _: Ok(lambda x: x * 2))
    y = 7
    left = u.ap(ReaderT(lambda _: Ok(y)))
    right = ReaderT(lambda _: Ok(lambda f: f(y))).ap(u)
    assert left.run({}) == right.run({})


# Monad laws
@pytest.mark.parametrize("env", [{"x": 1}, {"x": 2}])
def test_reader_t_monad_left_identity(env):
    f = lambda x: ReaderT(lambda e: Ok(x + e["x"]))
    x = 5
    assert ReaderT(lambda _: Ok(x)).bind(f).run(env) == f(x).run(env)


def test_reader_t_monad_right_identity():
    m = ReaderT(lambda e: Ok(e["x"]))
    assert m.bind(lambda a: ReaderT(lambda _: Ok(a))).run({"x": 3}) == m.run({"x": 3})


def test_reader_t_monad_associativity():
    m = ReaderT(lambda e: Ok(e["x"]))
    f = lambda x: ReaderT(lambda e: Ok(x + e["x"]))
    g = lambda y: ReaderT(lambda e: Ok(y * e["x"]))
    env = {"x": 4}
    left = m.bind(f).bind(g).run(env)
    right = m.bind(lambda x: f(x).bind(g)).run(env)
    assert left == right
