from __future__ import annotations

from dataclasses import dataclass

from s7dcls.error_paths import ErrorPath
from s7dcls.type_hints import resolve_tagged_union

from ..models import ValidateResult
from ..protocol import ValidatorProtocol, ValidatorWorkerProtocol


@dataclass(kw_only=True, frozen=True)
class TaggedUnionValidatorWorker(ValidatorWorkerProtocol):
    hub: ValidatorProtocol

    def __call__(self, *, value, dtype):
        spec = resolve_tagged_union(dtype)
        if spec is None:
            return None

        if value is None and spec.allow_none:
            return ValidateResult()

        if not hasattr(value, spec.field):
            raise TypeError(
                {
                    "value": value,
                    "expected_type": str(dtype),
                    "got_type": str(type(value)),
                }
            )

        tag = getattr(value, spec.field)
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

        self.hub(value=value, dtype=branch)
        return ValidateResult()


__all__ = ["TaggedUnionValidatorWorker"]
