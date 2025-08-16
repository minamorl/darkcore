from darkcore.state_t import StateT
from darkcore.result import Ok, Err

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
