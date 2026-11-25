# s7dcls

`Python >= 3.12` · `0 dependencies` · `PEP 561 (py.typed)`

## Install

```bash
pip install git+https://github.com/dusk5archiy/s7dcls.git
```

## Pipeline

```mermaid
flowchart LR
    Raw["Env / JSON / TOML"] --> DF["DictFetcher"]
    DF --> DT["DictTransform"]
    DT --> KR["DataclassKwargsResolver"]
    KR --> DS["DataclassSource"]
    DS --> DCF["ScaffoldDataclassFetcher"]
    DCF --> D["Dataclass"]
    D --> DH["DataclassDehydrator"]
    DH --> Out["dict[str, Any]"]
```

## Layout

| File | Role |
| :--- | :--- |
| `protocol.py` | Interface (`*Protocol`) |
| `mechanism.py` / `mechanism/` | Atomic implementations |
| `ops.py` | Closed combinators on same protocol |
| `scaffold.py` | Core algorithms, `Chain*`, `Hub*` |
| `standard.py` / `standard/` | Default presets (`.Args(...).build()`) |

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

class FirstMatch_(X -> Y | None):
    fn init(fs: [X -> Y | None])
    fn call(x: X) -> Y | None:
        for f in fs:
            x |> f as r
            if r is not None:
                r as return
        None as return

class Fallback_(X -> Y):
    fn init(fs: [X -> Y])
    fn call(x: X) -> Y:
        for f in fs:
            try:
                x |> f as return
            except (TypeError, ValueError):
                continue
        raise ...

class All_(X -> None):
    fn init(cs: [X -> None])
    fn call(x: X) -> None:
        for c in cs:
            x |> c

class Any_(X -> None):
    fn init(cs: [X -> None])
    fn call(x: X) -> None:
        for c in cs:
            try:
                x |> c
                return
            except (TypeError, ValueError):
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
        self |> spawner as worker: _Worker
        x |> worker as result: B
        map_result: B -> C
        result |> map_result as return

class Scaffold_(X -> Y):
    fn init(**deps)
    fn call(x: X) -> Y:
        (deps, x) |> core_algorithm as return

class Standard_(X -> Y):
    class Args:
        fn build() -> Standard_

    fn init(args: Args | None = None)
    fn call(x: X) -> Y
```

### Suffixes

```text
type _Emitter[T]   = () -> T
type _Transform[T] = T -> T
type _Gate[T]      = T -> T | None
type _Checker[T]   = T -> None | err
```

## Conventions

- Parameter order: `(value, dtype)` · `(data, datacls)`
- Errors: `TypeError({...})` / `ValueError({...})` structured `dict` (`path`)

## Examples

| File | Scope |
| :--- | :--- |
| [hydrate_dehydrate.py](examples/hydrate_dehydrate.py) | Hydrate & dehydrate |
| [layered_fetch.py](examples/layered_fetch.py) | TOML + ENV layered fetch |
| [coerce_validate_describe.py](examples/coerce_validate_describe.py) | Coerce, validate, schema |
| [custom_hub_coercer.py](examples/custom_hub_coercer.py) | Custom `HubCoercer` worker |
| [llm_tool_calling.py](examples/llm_tool_calling.py) | LLM JSON Schema + retry |
| [fastapi_adapter.md](examples/fastapi_adapter.md) | FastAPI body + HTTP 422 |

## Dev

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
uvx ruff format --check && uvx ruff check
uvx pyright && uvx basedpyright --level error
```
