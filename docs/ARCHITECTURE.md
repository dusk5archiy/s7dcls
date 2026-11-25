# Architecture

## Layout

| File | Role |
| :--- | :--- |
| `protocol.py` | Interface (`*Protocol`) |
| `mechanism.py` / `mechanism/` | Atomic implementations |
| `ops.py` | Closed combinators on same protocol |
| `scaffold.py` | Core algorithms, `Chain*`, `Hub*` |
| `standard.py` / `standard/` | Default presets |

## Patterns

### Prefixes (`ops.py`)

```text
class Sequence_(T -> T):
    fn init(fs: [T -> T])
    fn call(x: T) -> T:
        for f in fs:
            x |> f as x
        x as return

class Aggregate_(A -> M):
    fn init(fs: [A -> M])
    fn call(x: A) -> M:
        (x |> f for f in fs) |> merge as return

class Decorated_(A -> B):
    fn init(f: A -> B, t: B -> B)
    fn call(x: A) -> B:
        x |> f |> t as return

class Tapped_(A -> B):
    fn init(f: A -> B, s: B -> None)
    fn call(x: A) -> B:
        x |> f as r
        r |> s
        r as return

class FirstMatch_(X -> Y | None):
    fn init(fs: [X -> Y | None])
    fn call(x: X) -> Y | None:
        for f in fs:
            x |> f as r
            if r is not None:
                r as return
        None as return

class Default_(A -> B):
    fn init(f: A -> B | None, default: A -> B)
    fn call(x: A) -> B:
        x |> f as r
        if r is not None:
            r as return
        x |> default as return

class Fallback_(X -> Y):
    fn init(fs: [X -> Y], E: [Exception])
    fn call(x: X) -> Y:
        for f in fs:
            try:
                x |> f as return
            except E:
                continue
        raise ...

class Keyed_[K](A -> B):
    fn init(key_of: A -> K, handlers: {K: A -> B}, default: (A -> B) | None)
    fn call(x: A) -> B:
        x |> key_of as k
        if k in handlers:
            x |> handlers[k] as return
        if default is not None:
            x |> default as return
        raise ...

class All_(X -> None):
    fn init(cs: [X -> None])
    fn call(x: X) -> None:
        for c in cs:
            x |> c

class Any_(X -> None):
    fn init(cs: [X -> None], E: [Exception])
    fn call(x: X) -> None:
        for c in cs:
            try:
                x |> c
                return
            except E:
                continue
        raise ...
```

### Prefixes (`scaffold.py` & `standard.py`)

```text
class Chain_[B](A -> C):
    fn init(f: A -> B, g: B -> C)
    fn call(x: A) -> C:
        x |> f |> g as return

class Hub_[B](A -> C):
    type HubProtocol = A -> C
    type _Worker     = A -> B
    type _Spawner    = HubProtocol -> _Worker

    fn init(spawner: _Spawner)
    fn call(x: A) -> C:
        late worker: _Worker

        fn _hub(a: A) -> C:
            map_result: B -> C
            a |> worker |> map_result as return

        _hub |> spawner as worker
        x |> _hub as return

class Scaffold_(X -> Y):
    fn init(**deps)
    fn call(x: X) -> Y:
        (deps, x) |> core_algorithm as return

class Standard_(X -> Y):
    fn init(**config)
    fn call(x: X) -> Y:
        config |> build_default as pipeline
        x |> pipeline as return
```

### Suffixes

```text
type _Emitter[T]     = () -> T
type _Function[X, Y] = X -> Y
type _Transform[T]   = T -> T
type _Swallower[T]   = T -> None
type _Gate[T]        = T -> T | None
type _Checker[T]     = T -> None | err
```

## Conventions

- Construction: frozen `@dataclass(kw_only=True, frozen=True)` by default; optional nested `.Args(...).build()` idiom for classes that pre-build internal objects in `init` (e.g. `self.parent`, `self.worker`)
- Parameter order: `(value, dtype)` · `(data, datacls)`
- Errors: `TypeError({...})` / `ValueError({...})` structured `dict` (`path`)
