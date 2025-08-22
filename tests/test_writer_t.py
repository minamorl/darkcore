from darkcore.writer_t import WriterT
from darkcore.result import Ok, Err
import pytest

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


# Functor laws
def test_writer_t_functor_identity():
    w = WriterT(Ok((3, ["log"])))
    assert w.fmap(lambda a: a).run == w.run


def test_writer_t_functor_composition():
    w = WriterT(Ok((2, ["log"])))
    f = lambda x: x + 1
    g = lambda x: x * 2
    assert w.fmap(lambda x: f(g(x))).run == w.fmap(g).fmap(f).run


# Applicative laws
def test_writer_t_applicative_identity():
    v = WriterT(Ok((5, ["v"])))
    pure_id = WriterT(Ok((lambda x: x, [])))
    assert pure_id.ap(v).run == v.run


def test_writer_t_applicative_homomorphism():
    f = lambda x: x + 1
    x = 3
    left = WriterT(Ok((f, []))).ap(WriterT(Ok((x, []))))
    right = WriterT(Ok((f(x), [])))
    assert left.run == right.run


def test_writer_t_applicative_interchange():
    u = WriterT(Ok((lambda x: x * 2, ["f"])))
    y = 7
    left = u.ap(WriterT(Ok((y, []))))
    right = WriterT(Ok((lambda f: f(y), []))).ap(u)
    assert left.run == right.run


# Monad laws
def test_writer_t_monad_left_identity():
    f = lambda x: WriterT(Ok((x + 1, ["f"])))
    x = 5
    assert WriterT(Ok((x, []))).bind(f).run == f(x).run


def test_writer_t_monad_right_identity():
    m = WriterT(Ok((4, ["m"])))
    assert m.bind(lambda a: WriterT(Ok((a, [])))).run == m.run


def test_writer_t_monad_associativity():
    m = WriterT(Ok((1, ["m"])))
    f = lambda x: WriterT(Ok((x + 1, ["f"])))
    g = lambda y: WriterT(Ok((y * 2, ["g"])))
    left = m.bind(f).bind(g).run
    right = m.bind(lambda x: f(x).bind(g)).run
    assert left == right
