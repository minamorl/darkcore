from __future__ import annotations
from typing import Callable, Generic, TypeVar, Any, cast
from .core import Monad, MonadOpsMixin

A = TypeVar("A")
B = TypeVar("B")


class Result(MonadOpsMixin[A], Monad[A], Generic[A]):
    """
    Result は構造的に Monad を満たす成功/失敗の直和型。
    fmap は具象側で実装し、ここではシグネチャだけ宣言する。
    """
    def fmap(self, f: Callable[[A], B]) -> "Result[B]":  # 宣言のみ
        raise NotImplementedError

    def map(self, f: Callable[[A], B]) -> "Result[B]":
        return self.fmap(f)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Result) and self.__dict__ == other.__dict__

class Ok(Result[A]):
    def __init__(self, value: A) -> None:
        self.value = value

    @classmethod
    def pure(cls, value: A) -> "Result[A]":
        return Ok(value)

    def fmap(self, f: Callable[[A], B]) -> "Result[B]":
        return Ok(f(self.value))

    # 基底 Monad と同じシグネチャにする（LSP 違反を避ける）
    def bind(self, f: Callable[[A], Monad[B]]) -> Monad[B]:
        return f(self.value)

    # self は「関数を包んだ Ok」であることを要求
    def ap(self: "Ok[Callable[[A], B]]", fa: "Result[A]") -> "Result[B]":
        if isinstance(fa, Ok):
            func = self.value  # Callable[[A], B]
            return Ok(func(fa.value))
        return cast(Result[B], fa)  # Err はそのまま伝播

    def __repr__(self) -> str:
        return f"Ok({self.value!r})"


class Err(Result[A]):
    def __init__(self, error: str) -> None:
        self.error = error

    @classmethod
    def pure(cls, value: A) -> "Result[A]":
        # pure は成功側へ
        return Ok(value)

    def fmap(self, f: Callable[[A], B]) -> "Result[B]":
        # 失敗はそのまま（型的には B へキャストが必要）
        return cast(Result[B], self)

    def bind(self, f: Callable[[A], Monad[B]]) -> Monad[B]:
        # 失敗はそのまま（型的には B へキャストが必要）
        return cast(Monad[B], self)

    def ap(self, fa: "Result[A]") -> "Result[B]":
        # 失敗はそのまま（B へキャスト）
        return cast(Result[B], self)

    def __repr__(self) -> str:
        return f"Err({self.error!r})"
