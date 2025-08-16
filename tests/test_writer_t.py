from darkcore.writer_t import WriterT
from darkcore.result import Ok, Err

def test_writer_t_lift_and_run():
    wt = WriterT.lift(Ok(42), [])
    assert wt.run == Ok((42, []))

def test_writer_t_basic_bind():
    w1 = WriterT(Ok((3, ["init"])))
    def step(x: int) -> WriterT[int, str]:
        return WriterT(Ok((str(x), ["to-str"])))
    w2 = w1 >> step
    assert w2.run == Ok(("3", ["init", "to-str"]))

def test_writer_t_err_propagates():
    wt = WriterT(Err("fail"))
    def step(x: int) -> WriterT[int, int]:
        return WriterT(Ok((x*2, ["doubled"])))
    res = wt >> step
    assert res.run == Err("fail")

def test_writer_t_composition():
    def step1(x: int) -> WriterT[int, int]:
        return WriterT(Ok((x+1, ["inc"])))
    def step2(x: int) -> WriterT[int, str]:
        return WriterT(Ok((f"val={x}", ["fmt"])))
    prog = WriterT(Ok((5, ["start"]))) >> step1 >> step2
    assert prog.run == Ok(("val=6", ["start", "inc", "fmt"]))
