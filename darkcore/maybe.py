from typing import Callable, Generic, Union, TypeVar
from .core import Monad, Applicative, Functor

A = TypeVar('A')
B = TypeVar('B')
C = TypeVar('C')

class Maybe(Generic[C], Functor[C], Monad[C]):
    def __init__(self, value: Union[C, None]) -> None:
        self._value = value

    @staticmethod
    def pure(value: C) -> 'Maybe[C]':
        return Maybe(value)

    def fmap(self, f: Callable[[C], B]) -> 'Maybe[B]':
        if self._value is None:
            return Maybe(None)
        else:
            return Maybe(f(self._value))

    map = fmap

    def ap(self, other: 'Maybe[C]') -> 'Maybe[B]':
        if not isinstance(other, Maybe):
            raise TypeError(f'ap expects Maybe, got {type(other).__name__}')
        if self._value is None or other._value is None:
            return Maybe(None)
        if not callable(self._value):
            raise TypeError(f'ap expects a callable in self, got {type(self._value).__name__}')
        return Maybe(self._value(other._value))

    def bind(self, f: Callable[[C], 'Monad[B]']) -> 'Maybe[B]':
        result = f(self._value) if self._value is not None else Maybe(None)
        if not isinstance(result, Maybe):
            raise TypeError(f'bind must return Maybe, got {type(result).__name__}')
        return result

    def is_nothing(self) -> bool:
        return self._value is None

    def is_just(self) -> bool:
        return self._value is not None

    def get_or_else(self, default: C) -> C:
        if self._value is None:
            return default
        else:
            return self._value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Maybe):
            return NotImplemented
        return self._value == other._value

    def __repr__(self) -> str:
        if self._value is None:
            return 'Nothing'
        else:
            return f'Just({self._value})'
