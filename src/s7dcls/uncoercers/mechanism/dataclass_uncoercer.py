from __future__ import annotations

from dataclasses import dataclass, is_dataclass
from typing import Any

from s7dcls.dataclass_dehydrators.protocol import DataclassDehydratorProtocol
from s7dcls.uncoercers.models import UncoerceResult
from s7dcls.uncoercers.protocol import UncoercerWorkerProtocol


@dataclass(kw_only=True, frozen=True)
class DataclassUncoercerWorker(UncoercerWorkerProtocol):
    dataclass_dehydrator: DataclassDehydratorProtocol

    def __call__(self, *, value: Any) -> UncoerceResult | None:
        if not is_dataclass(value) or isinstance(value, type):
            return None
        return UncoerceResult(value=self.dataclass_dehydrator(instance=value))


__all__ = ["DataclassUncoercerWorker"]
