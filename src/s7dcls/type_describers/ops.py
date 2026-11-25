from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

from s7dcls.dict_transforms.protocol import DictTransformProtocol

from .models import DescribeTypeResult
from .protocol import TypeDescriberProtocol, TypeDescriberWorkerProtocol


@dataclass(kw_only=True, frozen=True)
class FirstMatchTypeDescriberWorker(TypeDescriberWorkerProtocol):
    workers: Sequence[TypeDescriberWorkerProtocol]

    def __call__(self, *, dtype: Any) -> DescribeTypeResult | None:
        for worker in self.workers:
            result = worker(dtype=dtype)
            if result is not None:
                return result
        return None


@dataclass(kw_only=True, frozen=True)
class DecoratedTypeDescriber(TypeDescriberProtocol):
    type_describer: TypeDescriberProtocol
    dict_transform: DictTransformProtocol

    def __call__(self, *, dtype: Any) -> dict[str, Any]:
        return dict(self.dict_transform(self.type_describer(dtype=dtype)))


__all__ = ["DecoratedTypeDescriber", "FirstMatchTypeDescriberWorker"]
