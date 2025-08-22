from darkcore.state_t import StateT
from darkcore.result import Ok, Err
import pytest

def test_state_t_lift_and_run():
    st = StateT.lift(Ok(42))
    result = st.run(0)
    assert result == Ok((42, 0))

def test_state_t_basic_bind():
    inc = StateT(lambda s: Ok((s, s+1)))
    prog = inc >> (lambda x: StateT(lambda s: Ok((x+s, s))))
    result = prog.run(1)
    # initial state = 1, inc -> (1,2), then x=1, s=2 -> (3,2)
    assert result == Ok((3, 2))

def test_state_t_err_propagates():
    st = StateT(lambda s: Err("fail"))
    prog = st >> (lambda x: StateT(lambda s: Ok((x*2, s))))
    result = prog.run(10)
    assert result == Err("fail")

def test_state_t_composition():
    def step1(x: int) -> StateT[int, int]:
        return StateT(lambda s: Ok((x+1, s+1)))

    def step2(x: int) -> StateT[int, str]:
        return StateT(lambda s: Ok((f"val={x}, state={s}", s*2)))

    prog = StateT(lambda s: Ok((s, s))) >> step1 >> step2
    result = prog.run(5)
    assert result == Ok(("val=6, state=6", 12))


# Functor laws
@pytest.mark.parametrize("s", [0, 1])
def test_state_t_functor_identity(s):
    st = StateT(lambda state: Ok((state + 1, state)))
    assert st.fmap(lambda a: a).run(s) == st.run(s)


@pytest.mark.parametrize("s", [2])
def test_state_t_functor_composition(s):
    st = StateT(lambda state: Ok((state, state)))
    f = lambda x: x + 3
    g = lambda x: x * 2
    lhs = st.fmap(lambda x: f(g(x)))
    rhs = st.fmap(g).fmap(f)
    assert lhs.run(s) == rhs.run(s)


# Applicative laws
@pytest.mark.parametrize("s", [0])
def test_state_t_applicative_identity(s):
    v = StateT(lambda state: Ok((state + 2, state)))
    pure_id = StateT(lambda state: Ok((lambda x: x, state)))
    assert pure_id.ap(v).run(s) == v.run(s)


def test_state_t_applicative_homomorphism():
    f = lambda x: x + 1
    x = 3
    left = StateT(lambda s: Ok((f, s))).ap(StateT(lambda s: Ok((x, s))))
    right = StateT(lambda s: Ok((f(x), s)))
    assert left.run(0) == right.run(0)


def test_state_t_applicative_interchange():
    u = StateT(lambda s: Ok((lambda x: x * 2, s)))
    y = 7
    left = u.ap(StateT(lambda s: Ok((y, s))))
    right = StateT(lambda s: Ok((lambda f: f(y), s))).ap(u)
    assert left.run(0) == right.run(0)


# Monad laws
@pytest.mark.parametrize("s", [0, 1])
def test_state_t_monad_left_identity(s):
    f = lambda x: StateT(lambda st: Ok((x + st, st)))
    x = 5
    assert StateT(lambda st: Ok((x, st))).bind(f).run(s) == f(x).run(s)


def test_state_t_monad_right_identity():
    m = StateT(lambda s: Ok((s + 1, s)))
    assert m.bind(lambda a: StateT(lambda s: Ok((a, s)))).run(0) == m.run(0)


def test_state_t_monad_associativity():
    m = StateT(lambda s: Ok((s + 1, s)))
    f = lambda x: StateT(lambda s: Ok((x * 2, s)))
    g = lambda y: StateT(lambda s: Ok((y - 1, s)))
    left = m.bind(f).bind(g).run(0)
    right = m.bind(lambda x: f(x).bind(g)).run(0)
    assert left == right
