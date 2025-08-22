from darkcore.writer import Writer

def test_match_writer():
    w = Writer(3, ["a"], empty=list, combine=lambda a, b: a + b)
    match w:
        case Writer(v, log=ls):
            assert v == 3 and ls == ["a"]
        case _:
            assert False, "unreachable"
