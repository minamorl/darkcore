from darkcore.result import Ok, Err

def test_match_result_ok_err():
    def handle(r):
        match r:
            case Ok(v) if v > 10:
                return ("ok-big", v)
            case Ok(v):
                return ("ok", v)
            case Err(e):
                return ("err", e)
    assert handle(Ok(5)) == ("ok", 5)
    assert handle(Ok(42)) == ("ok-big", 42)
    assert handle(Err("x")) == ("err", "x")
