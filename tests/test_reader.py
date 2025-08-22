from darkcore.reader import Reader


def test_reader_basic():
    r = Reader(lambda env: env + 1)
    assert r.run(10) == 11


def test_reader_map_operator():
    r = Reader(lambda env: env) | (lambda x: x + 1)
    assert r.run(2) == 3


def test_reader_bind():
    r = Reader(lambda env: env * 2)
    s = r >> (lambda x: Reader(lambda env: x + env))
    # env=3 のとき: r=6, その後 f(6) = Reader(lambda env: 6+env)=9
    assert s.run(3) == 9


def test_reader_ap_operator():
    rf = Reader(lambda env: lambda x: x + env)
    rx = Reader(lambda env: env * 2)
    r = rf @ rx
    assert r.run(3) == 9
