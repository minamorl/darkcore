from darkcore.reader import Reader

def test_reader_basic():
    r = Reader(lambda env: env + 1)
    assert r.run(10) == 11

def test_reader_bind():
    r = Reader(lambda env: env * 2)
    s = r.bind(lambda x: Reader(lambda env: x + env))
    # env=3 のとき: r=6, その後 f(6) = Reader(lambda env: 6+env)=9
    assert s.run(3) == 9
