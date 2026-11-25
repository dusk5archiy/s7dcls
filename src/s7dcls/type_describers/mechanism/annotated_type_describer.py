from __future__ import annotations

from dataclasses import dataclass
from typing import Annotated, Any, get_args, get_origin

from s7dcls.value_checkers.mechanism import (
    Ge,
    Gt,
    IntervalRangeValueChecker,
    Le,
    Lt,
    MaxLen,
    MinLen,
    MultipleOf,
    NonEmptyStr,
    RegexMatch,
    UniqueItems,
)

from ..models import DescribeTypeResult
from ..protocol import TypeDescriberProtocol, TypeDescriberWorkerProtocol


@dataclass(kw_only=True, frozen=True)
class AnnotatedTypeDescriberWorker(TypeDescriberWorkerProtocol):
    hub: TypeDescriberProtocol

    def __call__(self, *, dtype: Any) -> DescribeTypeResult | None:
        if get_origin(dtype) is not Annotated:
            return None

        base_type, *extras = get_args(dtype)
        schema = dict(self.hub(dtype=base_type))

        for extra in extras:
            if isinstance(extra, IntervalRangeValueChecker):
                schema["min"] = extra.min
                schema["max"] = extra.max
            elif isinstance(extra, Ge):
                schema["min"] = extra.limit
            elif isinstance(extra, Gt):
                schema["gt"] = extra.limit
            elif isinstance(extra, Le):
                schema["max"] = extra.limit
            elif isinstance(extra, Lt):
                schema["lt"] = extra.limit
            elif isinstance(extra, MultipleOf):
                schema["multiple_of"] = extra.step
            elif isinstance(extra, MinLen):
                schema["min_length"] = extra.limit
            elif isinstance(extra, MaxLen):
                schema["max_length"] = extra.limit
            elif isinstance(extra, UniqueItems):
                schema["unique_items"] = True
            elif isinstance(extra, NonEmptyStr):
                schema["non_empty"] = True
            elif isinstance(extra, RegexMatch):
                schema["pattern"] = extra.pattern

        return DescribeTypeResult(schema=schema)


__all__ = ["AnnotatedTypeDescriberWorker"]
