from darkcore.writer import Writer

def test_writer_bind_and_tell():
    w = Writer.pure(3).tell("start").bind(lambda x: Writer(x+1, ["inc"]))
    assert w.value == 4
    assert w.log == ["start", "inc"]

def test_writer_fmap():
    w = Writer(5, ["init"]).fmap(lambda x: x * 2)
    assert w == Writer(10, ["init"])
