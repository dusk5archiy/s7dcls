from __future__ import annotations

import ast
import inspect
import textwrap
from dataclasses import dataclass, fields, is_dataclass
from functools import lru_cache
from typing import Any


@dataclass(kw_only=True, frozen=True)
class DataclassDocstrings:
    class_doc: str | None
    field_docs: dict[str, str]


def _extract_from_ast(datacls: type[Any]) -> tuple[str | None, dict[str, str]] | None:
    try:
        source = textwrap.dedent(inspect.getsource(datacls))
        tree = ast.parse(source)
    except (OSError, TypeError, SyntaxError):
        return None

    class_def = next(
        (node for node in tree.body if isinstance(node, ast.ClassDef)),
        None,
    )
    if class_def is None:
        return None

    class_doc = ast.get_docstring(class_def)
    field_docs: dict[str, str] = {}
    body = class_def.body
    for idx, stmt in enumerate(body[:-1]):
        next_stmt = body[idx + 1]
        if not (
            isinstance(next_stmt, ast.Expr)
            and isinstance(next_stmt.value, ast.Constant)
            and isinstance(next_stmt.value.value, str)
        ):
            continue

        target_name: str | None = None
        if isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name):
            target_name = stmt.target.id
        elif (
            isinstance(stmt, ast.Assign)
            and len(stmt.targets) == 1
            and isinstance(stmt.targets[0], ast.Name)
        ):
            target_name = stmt.targets[0].id

        if target_name is not None:
            cleaned = inspect.cleandoc(next_stmt.value.value)
            if cleaned:
                field_docs[target_name] = cleaned

    return class_doc, field_docs


@lru_cache(maxsize=256)
def get_cached_dataclass_docstrings(datacls: type[Any]) -> DataclassDocstrings:
    if not isinstance(datacls, type) or not is_dataclass(datacls):
        raise TypeError({"datacls": str(datacls), "reason": "must be a dataclass"})

    ast_result = _extract_from_ast(datacls)
    if ast_result is not None:
        class_doc, field_docs = ast_result
    else:
        raw_doc = datacls.__doc__
        if raw_doc and not raw_doc.startswith(f"{datacls.__name__}("):
            class_doc = inspect.cleandoc(raw_doc)
        else:
            class_doc = None
        field_docs = {}

    merged_field_docs = dict(field_docs)
    for definition in fields(datacls):
        meta_doc = definition.metadata.get("description")
        if isinstance(meta_doc, str) and meta_doc.strip():
            merged_field_docs[definition.name] = inspect.cleandoc(meta_doc)

    return DataclassDocstrings(class_doc=class_doc, field_docs=merged_field_docs)


__all__ = ["DataclassDocstrings", "get_cached_dataclass_docstrings"]
