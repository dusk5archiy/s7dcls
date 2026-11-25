from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from s7dcls.coercers.models import CoerceResult
from s7dcls.coercers.protocol import CoercerProtocol, JsonCoercerWorkerProtocol
from s7dcls.error_paths import ErrorPath
from s7dcls.type_hints import resolve_tagged_union


@dataclass(kw_only=True, frozen=True)
class TaggedUnionCoercerWorker(JsonCoercerWorkerProtocol):
    hub: CoercerProtocol

    def can_handle(self, *, dtype: Any) -> bool:
        return resolve_tagged_union(dtype) is not None

    def __call__(self, *, value: Any, dtype: Any) -> CoerceResult[Any] | None:
        spec = resolve_tagged_union(dtype)
        if spec is None:
            return None

        if value is None and spec.allow_none:
            return CoerceResult(value=None)

        if isinstance(value, Mapping):
            if spec.field not in value:
                raise ValueError({"expected_type": str(dtype), "missing": [spec.field]})
            tag = value[spec.field]
            branch = spec.branches.get((type(tag), tag))
            if branch is None:
                with ErrorPath(segment=spec.field):
                    raise ValueError(
                        {
                            "value": tag,
                            "expected_type": str(dtype),
                            "allowed": list(spec.allowed),
                        }
                    )
            return CoerceResult(value=self.hub(value=value, dtype=branch))

        if hasattr(value, spec.field):
            tag = getattr(value, spec.field)
            branch = spec.branches.get((type(tag), tag))
            if branch is not None:
                return CoerceResult(value=self.hub(value=value, dtype=branch))

        raise TypeError(
            {
                "value": value,
                "expected_type": str(dtype),
                "got_type": str(type(value)),
            }
        )


__all__ = ["TaggedUnionCoercerWorker"]
