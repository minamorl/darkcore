#!/bin/bash
set -e

# --- core.py ---
sed -i 's/def pure(cls, value: A) -> Self:/def pure(cls, value: A) -> "Monad[A]":/' darkcore/core.py
sed -i 's/def bind(self, f: Callable\[\[A\], Self\]) -> Self:/def bind(self, f: Callable[[A], "Monad[B]"]) -> "Monad[B]":/' darkcore/core.py

# --- maybe.py ---
sed -i 's/def get_or_else(self, default: Optional\[A\]) -> A:/def get_or_else(self, default: A) -> A:/' darkcore/maybe.py

# --- either.py ---
sed -i 's/def pure(cls, value: A) -> Right\[A\]/def pure(cls, value: A) -> "Either[A]"/' darkcore/either.py

# --- result.py ---
sed -i 's/def pure(cls, value: A) -> Ok\[A\]/def pure(cls, value: A) -> "Result[A]"/' darkcore/result.py
# unify Err.pure too
sed -i 's/def pure(cls, value: A) -> Ok\[A\]/def pure(cls, value: A) -> "Result[A]"/' darkcore/result.py

# --- writer_t.py ---
sed -i 's/def __init__(self, run: Monad\[tuple\[A, list\[W\]\]\]) -> None:/def __init__(self, run: Monad[tuple[A, list[W]]]) -> None:/' darkcore/writer_t.py
sed -i 's/def lift(cls, monad: Monad\[A\], empty_log: List\[W\]) -> WriterT\[A, W\]:/def lift(cls, monad: Monad[A], empty_log: list[W]) -> "WriterT[A, W]":/' darkcore/writer_t.py
sed -i 's/def bind(self, f: callable/def bind(self, f: Callable/' darkcore/writer_t.py
sed -i 's/def __rshift__(self, f: callable/def __rshift__(self, f: Callable/' darkcore/writer_t.py

# --- state_t.py ---
sed -i 's/def lift(cls, monad: Monad\[A\]) -> StateT\[S, A\]:/def lift(cls, monad: Monad[A]) -> "StateT[S, A]":/' darkcore/state_t.py
sed -i 's/def bind(self, f: Callable\[\[A\], StateT\[S, B\]\]) -> StateT\[S, B\]:/def bind(self, f: Callable[[A], "StateT[S, B]"]) -> "StateT[S, B]":/' darkcore/state_t.py
sed -i 's/def __call__(self, state: S):/def __call__(self, state: S) -> Monad[tuple[A, S]]:/' darkcore/state_t.py

# --- reader_t.py ---
sed -i 's/def bind(self, f: Callable\[\[A\], ReaderT\[R, B\]\]) -> ReaderT\[R, B\]:/def bind(self, f: Callable[[A], "ReaderT[R, B]"]) -> "ReaderT[R, B]":/' darkcore/reader_t.py
sed -i 's/def __call__(self, env: R):/def __call__(self, env: R) -> Monad[A]:/' darkcore/reader_t.py
