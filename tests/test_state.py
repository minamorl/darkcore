from darkcore.state import State

def test_state_basic():
    inc = State(lambda s: (s, s+1))
    result, final = inc.run(0)
    assert result == 0 and final == 1

def test_state_bind():
    inc = State(lambda s: (s, s+1))
    prog = inc.bind(lambda x: State(lambda s: (x+s, s)))
    result, final = prog.run(1)
    assert (result, final) == (3, 2)

def test_state_get_put():
    prog = State.get().bind(lambda s: State.put(s+10).bind(lambda _: State.pure(s)))
    result, final = prog.run(5)
    assert result == 5 and final == 15
