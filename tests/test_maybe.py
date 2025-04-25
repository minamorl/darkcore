from darkcore.maybe import Maybe

def test_maybe_bind_success():
    m = Maybe(3)
    result = (
        m.bind(lambda x: Maybe(x + 1))
         .bind(lambda x: Maybe(x * 2))
    )
    assert result.value == 8

def test_maybe_bind_none():
    m = Maybe(None)
    result = (
        m.bind(lambda x: Maybe(x + 1))
         .bind(lambda x: Maybe(x * 2))
    )
    assert result.value is None
