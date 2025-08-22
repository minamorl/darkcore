from darkcore.either import Right, Left

def test_match_either():
    def handle(x):
        match x:
            case Right(v):
                return ("right", v)
            case Left(e):
                return ("left", e)
    assert handle(Right(7)) == ("right", 7)
    assert handle(Left("e")) == ("left", "e")
