from typing import Callable, Generic, TypeVar, Any, cast
from darkcore.core import Monad
from darkcore.maybe import Maybe

C = TypeVar('C')
B = TypeVar('B')

class MaybeT(Generic[C]):
    """
    MaybeT: Lightweight Maybe transformer.
    No strict Monad adherence.
    """

    def __init__(self, run: Any) -> None:
        self.run = run  # run is assumed to be Monad[Maybe[C]]

    @staticmethod
    def lift(monad: Any) -> 'MaybeT[Any]':
        return MaybeT(monad.bind(lambda x: monad.pure(Maybe(x))))

    def map(self, f: Callable[[Any], Any]) -> 'MaybeT[Any]':
        return MaybeT(
            self.run.bind(lambda maybe:
                self.run.pure(maybe.map(f))  # maybe.fmap(f)も同じ
            )
        )

    def ap(self: 'MaybeT[Callable[[C], B]]', fa: 'MaybeT[C]') -> 'MaybeT[B]':
        return MaybeT(
            self.run.bind(lambda mf:  # ← self（関数）が先
                fa.run.bind(lambda mx:  # ← fa（引数）が後
                    self.run.pure(mf.ap(mx))
                )
            )
        )

    def bind(self, f: Callable[[C], 'MaybeT[B]']) -> 'MaybeT[B]':
        def step(maybe: Any) -> Any:
            if maybe.is_nothing():
                return self.run.pure(Maybe(None))
            else:
                return f(cast(C, maybe.get_or_else(None))).run
    
        return MaybeT(self.run.bind(step))
