# darkcore

**darkcore** is a lightweight functional programming toolkit for Python.  
It brings **Functor / Applicative / Monad** abstractions, classic monads like **Maybe, Either/Result, Reader, Writer, State**,  
and an expressive **operator DSL** (`|`, `>>`, `@`) that makes Python feel almost like Haskell.

---

## ✨ Features

- Functor / Applicative / Monad base abstractions
- Core monads implemented:
  - `Maybe` — handle missing values
  - `Either` / `Result` — safe error handling
  - `Validation` — accumulate multiple errors
  - `Reader` — dependency injection / environment
  - `Writer` — accumulate logs
  - `State` — stateful computations
- Monad transformers: `MaybeT`, `ResultT`, `ReaderT`, `StateT`, `WriterT`
- Utilities: `traverse`/`sequence`, Applicative combinators
- Advanced monads: `RWST` (Reader-Writer-State)
- Operator overloads for concise DSL-style code:
  - `|` → `fmap` (map)
  - `>>` → `bind` (flatMap)
  - `@` → `ap` (applicative apply)
- High test coverage, Monad law tests included

---

## 🚀 Installation

```bash
pip install darkcore
```

(or use Poetry)

---

## 🧪 Quick Examples

### Maybe

```python
from darkcore.maybe import Maybe

m = Maybe(3) | (lambda x: x+1) >> (lambda y: Maybe(y*2))
print(m)  # Just(8)

n = Maybe(None) | (lambda x: x+1)
print(n)  # Nothing
```

---

### Result

```python
from darkcore.result import Ok, Err

def parse_int(s: str):
    try:
        return Ok(int(s))
    except ValueError:
        return Err(f"invalid int: {s}")

res = parse_int("42") >> (lambda x: Ok(x * 2))
print(res)  # Ok(84)

res2 = parse_int("foo") >> (lambda x: Ok(x * 2))
print(res2)  # Err("invalid int: foo")
```

---

### Validation: accumulate errors via Applicative

```python
from darkcore.validation import Success, Failure

def positive(x: int):
    return Failure(["non-positive"]) if x <= 0 else Success(x)

v = Success(lambda a: lambda b: a + b).ap(positive(-1)).ap(positive(0))
print(v)  # Failure(['non-positive', 'non-positive'])

# Result would stop at the first failure
```

Validation is primarily intended for Applicative composition; `bind` short-circuits like `Result` and is not recommended for error accumulation scenarios.

---

### Reader

```python
from darkcore.reader import Reader

get_user = Reader(lambda env: env["user"])
greet = get_user | (lambda u: f"Hello {u}")

print(greet.run({"user": "Alice"}))  # "Hello Alice"
```

---

### Writer

```python
from darkcore.writer import Writer

# list log by default
w = Writer.pure(3).tell(["start"]) >> (lambda x: Writer(x + 1, ["inc"]))
print(w)  # Writer(4, log=['start', 'inc'])

# for non-``list`` logs, pass ``empty`` and ``combine`` explicitly
# ``empty`` provides the identity element and ``combine`` appends logs
w2 = Writer("hi", empty=str, combine=str.__add__).tell("!")
print(w2)  # Writer('hi', log='!')

# omitting these for a non-``list`` log raises ``TypeError``
try:
    Writer("hi", "!")  # missing empty/combine
except TypeError:
    print("expected TypeError")
```

---

### State

```python
from darkcore.state import State

inc = State(lambda s: (s, s+1))
prog = inc >> (lambda x: State(lambda s: (x+s, s)))

print(prog.run(1))  # (3, 2)
```

### Traverse utilities

```python
from darkcore.traverse import traverse_result
from darkcore.result import Ok, Err

def parse_int(s: str):
    try:
        return Ok(int(s))
    except ValueError:
        return Err(f"bad: {s}")

print(traverse_result(["1", "2"], parse_int))  # Ok([1, 2])
print(traverse_result(["1", "x"], parse_int))  # Err("bad: x")
```

`Result` short-circuits on the first `Err` in `traverse_*` / `sequence_*`, whereas `Validation` accumulates errors under Applicative composition.

### RWST

```python
from darkcore.rwst import RWST
from darkcore.result import Ok

combine = lambda a, b: a + b

action = RWST.ask(Ok.pure, combine=combine, empty=list).bind(
    lambda env: RWST.tell([env], Ok.pure, combine=combine, empty=list)
)

print(action(1, 0))  # Ok(((None, 0), [1]))
```

### Operator DSL

```python
from darkcore.maybe import Maybe

mf = Maybe(lambda x: x * 2)
mx = Maybe(4)
print((mf @ mx) | (lambda x: x + 1))  # Just(9)
```

---

## 📖 Integration Example

```python
from darkcore.reader import Reader
from darkcore.writer import Writer
from darkcore.state import State
from darkcore.result import Ok, Err

# Reader: get user from environment
get_user = Reader(lambda env: env.get("user"))

# Result: validate existence
to_result = lambda user: Err("no user") if user is None else Ok(user)

# Writer: log user
log_user = lambda user: Writer(user, [f"got user={user}"])

# State: update counter
update_state = lambda user: State(lambda s: (f"{user}@{s}", s+1))

env = {"user": "alice"}

user = get_user.run(env)
res = to_result(user) >> (lambda u: Ok(log_user(u)))
writer = res.value
print(writer.log)  # ['got user=alice']

out, s2 = update_state(writer.value).run(42)
print(out, s2)  # alice@42 43
```

---

## Why?

- **Safer business code**  
  - Avoid nested `try/except` and `if None` checks  
  - Express computations declaratively with monads  
- **Educational value**  
  - Learn Haskell/FP concepts hands-on in Python  
- **Expressive DSL**  
  - `|`, `>>`, `@` make pipelines concise and clear  

---

## Development

```bash
git clone https://github.com/minamorl/darkcore
cd darkcore
poetry install
poetry run pytest -v --cov=darkcore
```

---

## License

MIT
