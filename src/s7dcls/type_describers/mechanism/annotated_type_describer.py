from __future__ import annotations

from dataclasses import dataclass
from typing import Annotated, Any, get_args, get_origin

from s7dcls.value_checkers.mechanism import (
    Ge,
    Gt,
    IntervalRangeValueChecker,
    Le,
    Lt,
    NonEmptyStr,
    RegexMatch,
)

from ..models import DescribeTypeResult
from ..protocol import StrictTypeDescriberProtocol, TypeDescriberProtocol


@dataclass(kw_only=True, frozen=True)
class AnnotatedTypeDescriber(TypeDescriberProtocol):
    inner_type_describer: StrictTypeDescriberProtocol

    def __call__(self, *, dtype: Any) -> DescribeTypeResult | None:
        if get_origin(dtype) is not Annotated:
            return None

        base_type, *extras = get_args(dtype)
        schema = dict(self.inner_type_describer(dtype=base_type).schema)

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
            elif isinstance(extra, NonEmptyStr):
                schema["non_empty"] = True
            elif isinstance(extra, RegexMatch):
                schema["pattern"] = extra.pattern

        return DescribeTypeResult(schema=schema)


__all__ = ["AnnotatedTypeDescriber"]
