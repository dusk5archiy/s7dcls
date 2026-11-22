from __future__ import annotations

from dataclasses import dataclass
from typing import Any, get_args, get_origin

from ..models import DescribeTypeResult
from ..protocol import StrictTypeDescriberProtocol, TypeDescriberProtocol


@dataclass(kw_only=True, frozen=True)
class TupleTypeDescriber(TypeDescriberProtocol):
    inner_type_describer: StrictTypeDescriberProtocol

    def __call__(self, *, dtype: Any) -> DescribeTypeResult | None:
        if get_origin(dtype) is not tuple:
            return None

        args = get_args(dtype)
        if len(args) == 2 and args[1] is Ellipsis:
            return DescribeTypeResult(
                schema={
                    "type": "array",
                    "items": self.inner_type_describer(dtype=args[0]),
                }
            )
        if args:
            return DescribeTypeResult(
                schema={
                    "type": "tuple",
                    "items": [
                        self.inner_type_describer(dtype=arg) for arg in args
                    ],
                }
            )
        return DescribeTypeResult(schema={"type": "array", "items": {"type": "any"}})


__all__ = ["TupleTypeDescriber"]
