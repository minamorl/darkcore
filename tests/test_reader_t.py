from darkcore.result import Ok, Err
from darkcore.reader_t import ReaderT

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
