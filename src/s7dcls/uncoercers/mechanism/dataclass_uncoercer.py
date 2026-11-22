from __future__ import annotations

from dataclasses import dataclass, is_dataclass

from s7dcls.dataclass_dehydrators.protocol import DataclassDehydratorProtocol
from s7dcls.uncoercers.models import UncoerceResult
from s7dcls.uncoercers.protocol import StrictUncoercerProtocol, UncoercerProtocol


@dataclass(kw_only=True, frozen=True)
class DataclassUncoercer(UncoercerProtocol):
    inner_uncoercer: StrictUncoercerProtocol
    dataclass_dehydrator: DataclassDehydratorProtocol

    def __call__(self, *, value):
        if not is_dataclass(value) or isinstance(value, type):
            return None
        return UncoerceResult(
            value=self.dataclass_dehydrator(
                instance=value,
                uncoercer=self.inner_uncoercer,
            )
        )


__all__ = ["DataclassUncoercer"]
