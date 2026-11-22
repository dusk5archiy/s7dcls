from __future__ import annotations

from dataclasses import dataclass
from typing import Any, get_args, get_origin

from ..models import DescribeTypeResult
from ..protocol import StrictTypeDescriberProtocol, TypeDescriberProtocol


@dataclass(kw_only=True, frozen=True)
class ListTypeDescriber(TypeDescriberProtocol):
    inner_type_describer: StrictTypeDescriberProtocol

    def __call__(self, *, dtype: Any) -> DescribeTypeResult | None:
        if get_origin(dtype) is not list:
            return None

        args = get_args(dtype)
        items = (
            self.inner_type_describer(dtype=args[0])
            if args
            else {"type": "any"}
        )
        return DescribeTypeResult(schema={"type": "array", "items": items})


__all__ = ["ListTypeDescriber"]
