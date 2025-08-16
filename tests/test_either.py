from darkcore.either import Left, Right

def test_right_map_and_bind():
    r = Right(10)
    r2 = r.map(lambda x: x + 5)
    assert isinstance(r2, Right)
    assert r2.value == 15

    r3 = r.bind(lambda x: Right(x * 2))
    assert r3 == Right(20)

def test_left_propagates():
    l = Left("error")
    assert l.map(lambda x: x + 1) == l
    assert l.bind(lambda x: Right(x * 2)) == l

def test_monad_laws():
    f = lambda x: Right(x + 1)
    g = lambda x: Right(x * 2)
    x = 5
    # 左単位元
    assert Right.pure(x).bind(f) == f(x)
    # 右単位元
    m = Right(x)
    assert m.bind(Right.pure) == m
    # 結合律
    assert m.bind(f).bind(g) == m.bind(lambda y: f(y).bind(g))
