from darkcore.maybe import Maybe

def test_maybe_bind_success():
    m = Maybe(3)
    result = (
        m.bind(lambda x: Maybe(x + 1))
         .bind(lambda x: Maybe(x * 2))
    )
    assert result._value == 8

def test_maybe_bind_none():
    m = Maybe(None)
    result = (
        m.bind(lambda x: Maybe(x + 1))
         .bind(lambda x: Maybe(x * 2))
    )
    assert result._value is None

def test_maybe_ap_success():
    mf = Maybe(lambda x: x + 2)
    mx = Maybe(3)
    result = mx.ap(mf)
    assert result.get_or_else(0) == 5

def test_maybe_ap_none_function():
    mf = Maybe(None)
    mx = Maybe(3)
    result = mx.ap(mf)
    assert result.is_nothing()

def test_maybe_ap_none_value():
    mf = Maybe(lambda x: x + 2)
    mx = Maybe(None)
    result = mx.ap(mf)
    assert result.is_nothing()

def test_monad_left_identity():
    f = lambda x: Maybe(x + 1)
    x = 5
    assert Maybe.pure(x).bind(f) == f(x)

def test_monad_right_identity():
    m = Maybe(5)
    assert m.bind(Maybe.pure) == m

def test_monad_associativity():
    m = Maybe(5)
    f = lambda x: Maybe(x + 1)
    g = lambda x: Maybe(x * 2)
    assert m.bind(f).bind(g) == m.bind(lambda x: f(x).bind(g))
