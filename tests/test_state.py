from darkcore.state import State

from darkcore.state import State
import pytest


def test_state_basic():
    inc = State(lambda s: (s, s + 1))
    result, final = inc.run(0)
    assert result == 0 and final == 1


def test_state_map_operator():
    inc = State(lambda s: (s, s + 1))
    result, final = (inc | (lambda x: x + 1)).run(0)
    assert (result, final) == (1, 1)


def test_state_bind():
    inc = State(lambda s: (s, s + 1))
    prog = inc >> (lambda x: State(lambda s: (x + s, s)))
    result, final = prog.run(1)
    assert (result, final) == (3, 2)


def test_state_get_put():
    prog = State.get() >> (lambda s: State.put(s + 10) >> (lambda _: State.pure(s)))
    result, final = prog.run(5)
    assert result == 5 and final == 15


def test_state_ap_operator():
    sf = State(lambda s: (lambda x: x + s, s))
    sx = State(lambda s: (s, s + 1))
    result, final = (sf @ sx).run(1)
    assert (result, final) == (2, 2)


# Functor laws
@pytest.mark.parametrize("s", [0, 5])
def test_state_functor_identity(s):
    st = State(lambda state: (state + 1, state))
    assert (st | (lambda x: x)).run(s) == st.run(s)


@pytest.mark.parametrize("s", [1, 2])
def test_state_functor_composition(s):
    st = State(lambda state: (state, state))
    f = lambda x: x + 3
    g = lambda x: x * 4
    lhs = st | (lambda x: f(g(x)))
    rhs = (st | g) | f
    assert lhs.run(s) == rhs.run(s)


# Applicative laws
@pytest.mark.parametrize("s", [0, 3])
def test_state_applicative_identity(s):
    v = State(lambda state: (state + 2, state))
    assert (State.pure(lambda x: x) @ v).run(s) == v.run(s)


@pytest.mark.parametrize("s", [4])
def test_state_applicative_homomorphism(s):
    f = lambda x: x + 1
    x = 3
    left = State.pure(f) @ State.pure(x)
    right = State.pure(f(x))
    assert left.run(s) == right.run(s)


@pytest.mark.parametrize("s", [2])
def test_state_applicative_interchange(s):
    u = State.pure(lambda x: x * 2)
    y = 7
    left = u @ State.pure(y)
    right = State.pure(lambda f: f(y)) @ u
    assert left.run(s) == right.run(s)


# Monad laws
@pytest.mark.parametrize("s", [0, 1])
def test_state_monad_left_identity(s):
    f = lambda x: State(lambda st: (x + st, st))
    x = 5
    assert State.pure(x).bind(f).run(s) == f(x).run(s)


@pytest.mark.parametrize("s", [2, 3])
def test_state_monad_right_identity(s):
    m = State(lambda st: (st + 1, st))
    assert m.bind(State.pure).run(s) == m.run(s)


@pytest.mark.parametrize("s", [4])
def test_state_monad_associativity(s):
    m = State(lambda st: (st + 1, st))
    f = lambda x: State(lambda st: (x * 2, st))
    g = lambda y: State(lambda st: (y - 1, st))
    left = m.bind(f).bind(g)
    right = m.bind(lambda x: f(x).bind(g))
    assert left.run(s) == right.run(s)
