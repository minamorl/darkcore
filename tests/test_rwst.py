from darkcore.rwst import RWST
from darkcore.result import Ok


def run(rwst, r=0, s=0):
    return rwst(r, s)


def combine_list(a, b):
    return a + b


def test_rwst_extensional_equality_basic():
    combine = lambda a, b: a + b
    empty = list
    r1 = RWST(lambda r, s: Ok(((s + r, s), ["a"])), combine=combine, empty=empty)
    r2 = RWST(lambda r, s: Ok(((s + r, s), ["a"])), combine=combine, empty=empty)
    for env in [0, 1, 2]:
        for st in [0, 3]:
            assert r1.run(env, st) == r2.run(env, st)


def test_rwst_applicative_identity_extensional():
    combine = lambda a, b: a + b
    empty = list
    pure = Ok.pure
    fa = RWST.pure_with(pure, 5, combine=combine, empty=empty)
    identity = RWST.pure_with(pure, lambda x: x, combine=combine, empty=empty).ap(fa)
    for env in [0, 1]:
        for st in [2, 3]:
            assert identity.run(env, st) == fa.run(env, st)


def test_functor_applicative_monad_laws():
    empty = list
    pure = Ok.pure
    fa = RWST.pure_with(pure, 1, combine=combine_list, empty=empty)
    fb = RWST.pure_with(pure, 2, combine=combine_list, empty=empty)
    # Functor identity
    assert run(fa.fmap(lambda x: x)) == run(fa)
    # Applicative identity
    assert run(RWST.pure_with(pure, lambda x: x, combine=combine_list, empty=empty).ap(fa)) == run(fa)
    # Monad associativity
    f = lambda x: RWST.pure_with(pure, x + 1, combine=combine_list, empty=empty)
    g = lambda x: RWST.pure_with(pure, x * 2, combine=combine_list, empty=empty)
    left = run(fa.bind(f).bind(g))
    right = run(fa.bind(lambda x: f(x).bind(g)))
    assert left == right


def test_tell_put_ask():
    pure = Ok.pure
    empty = list
    action = RWST.ask(pure, combine=combine_list, empty=empty).bind(
        lambda env: RWST.tell([env], pure, combine=combine_list, empty=empty)
    )
    assert run(action, r=5, s=10) == Ok(((None, 10), [5]))

    put_action = RWST.put(42, pure, combine=combine_list, empty=empty)
    assert run(put_action, r=0, s=0) == Ok(((None, 42), []))


def test_log_associativity_str():
    pure = Ok.pure
    empty = lambda: ""
    combine = lambda a, b: a + b
    a = RWST.tell("a", pure, combine=combine, empty=empty)
    b = RWST.tell("b", pure, combine=combine, empty=empty)
    c = RWST.tell("c", pure, combine=combine, empty=empty)
    res1 = run(a.bind(lambda _: b).bind(lambda _: c), r=0, s=0)
    res2 = run(a.bind(lambda _: b.bind(lambda _: c)), r=0, s=0)
    assert res1 == res2 == Ok(((None, 0), "abc"))
