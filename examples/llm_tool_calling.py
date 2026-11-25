from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Annotated, Literal

from s7dcls import (
    Gt,
    NonEmptyStr,
    StandardJsonCoercer,
    StandardJsonSchemaDescriber,
)


@dataclass(kw_only=True, frozen=True)
class SearchTool:
    """Search knowledge base."""

    kind: Literal["search"]
    query: Annotated[str, NonEmptyStr()]
    top_k: Annotated[int, Gt(limit=0)] = 5


@dataclass(kw_only=True, frozen=True)
class CalcTool:
    """Evaluate a math expression."""

    kind: Literal["calc"]
    expression: Annotated[str, NonEmptyStr()]


type ToolCall = SearchTool | CalcTool


def parse_llm_tool(raw_json: str) -> ToolCall:
    coercer = StandardJsonCoercer.Args(collect_errors=True).build()
    try:
        return coercer(value=json.loads(raw_json), dtype=ToolCall)
    except ExceptionGroup as eg:
        feedback = [exc.args[0] for exc in eg.exceptions]
        raise ValueError({"retry_feedback": feedback}) from eg
    except (TypeError, ValueError) as exc:
        raise ValueError({"retry_feedback": [exc.args[0]]}) from exc


def main() -> None:
    json_schema_describer = StandardJsonSchemaDescriber.Args(
        include_docstrings=True
    ).build()
    tool_schema = json_schema_describer(dtype=ToolCall)
    print(json.dumps(tool_schema, indent=2))

    ok = parse_llm_tool('{"kind": "search", "query": "s7dcls", "top_k": 3}')
    assert ok == SearchTool(kind="search", query="s7dcls", top_k=3)

    try:
        parse_llm_tool('{"kind": "search", "query": "", "top_k": 0}')
    except ValueError as err:
        feedback = err.args[0]["retry_feedback"]
        assert len(feedback) == 2
        print("Retry feedback:", feedback)


if __name__ == "__main__":
    main()
