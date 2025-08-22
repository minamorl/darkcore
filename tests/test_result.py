from darkcore.result import Ok, Err

def test_ok_map_and_bind():
    r = Ok(3)
    r2 = r.map(lambda x: x + 1)
    assert r2 == Ok(4)

    r3 = r2.bind(lambda x: Ok(x * 2))
    assert r3 == Ok(8)

def test_err_propagates():
    e = Err("fail")
    assert e.map(lambda x: x + 1) == e
    assert e.bind(lambda x: Ok(x * 2)) == e

def test_result_laws():
    f = lambda x: Ok(x + 1)
    g = lambda x: Ok(x * 2)
    x = 7
    # 左単位元
    assert Ok.pure(x).bind(f) == f(x)
    # 右単位元
    m = Ok(x)
    assert m.bind(Ok.pure) == m
    # 結合律
    assert m.bind(f).bind(g) == m.bind(lambda y: f(y).bind(g))


def test_result_map_operator():
    assert (Ok(3) | (lambda x: x + 1)) == Ok(4)


def test_result_ap_operator():
    rf = Ok(lambda x: x + 1)
    rx = Ok(2)
    assert rf @ rx == Ok(3)
    assert Err("e") @ rx == Err("e")
