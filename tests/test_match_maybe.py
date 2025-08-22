from darkcore.maybe import Maybe

def test_match_maybe_value_none():
    def handle(m):
        match m:
            case Maybe(value=None):
                return "nothing"
            case Maybe(value=v) if v % 2:
                return ("odd", v)
            case Maybe(value=v):
                return ("even", v)
    assert handle(Maybe(None)) == "nothing"
    assert handle(Maybe(3)) == ("odd", 3)
    assert handle(Maybe(4)) == ("even", 4)
