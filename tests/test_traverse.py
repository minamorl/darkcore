from darkcore.maybe import Maybe
from darkcore.result import Ok, Err, Result
from darkcore.traverse import (
    sequence_maybe,
    sequence_result,
    traverse_maybe,
    traverse_result,
    liftA2,
    left_then,
    then_right,
)


def test_traverse_identity_maybe():
    xs = [1, 2, 3]
    assert traverse_maybe(xs, Maybe) == Maybe(xs)


def test_sequence_equivalence_maybe():
    xs = [Maybe(1), Maybe(2)]
    assert sequence_maybe(xs) == traverse_maybe(xs, lambda x: x)


def test_sequence_result_early_stop():
    xs: list[Result[int]] = [Ok(1), Err("e"), Ok(2)]
    assert sequence_result(xs) == Err("e")


def test_traverse_result_identity():
    xs = [1, 2]
    assert traverse_result(xs, Ok) == Ok(xs)


def test_liftA2_and_sequence():
    fa = Ok(2)
    fb = Ok(3)
    add = lambda a, b: a + b
    assert liftA2(add, fa, fb) == Ok(5)
    assert left_then(fa, fb) == Ok(2)
    assert then_right(fa, fb) == Ok(3)
