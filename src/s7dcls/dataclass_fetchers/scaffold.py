from __future__ import annotations

from dataclasses import MISSING, dataclass, fields
from typing import TYPE_CHECKING, cast

from s7dcls.dataclass_sources.protocol import DataclassSourceProtocol
from s7dcls.type_hints import resolve_dataclass_type

from .protocol import DataclassFetcherProtocol

if TYPE_CHECKING:
    from _typeshed import DataclassInstance


@dataclass(kw_only=True, frozen=True)
class ScaffoldDataclassFetcher(DataclassFetcherProtocol):
    source: DataclassSourceProtocol

    def __call__[T: DataclassInstance](self, *, datacls: type[T]) -> T:
        resolved = resolve_dataclass_type(datacls)
        actual_cls = resolved[0] if resolved is not None else datacls
        kwargs = self.source(datacls=datacls)
        missing = sorted(
            definition.name
            for definition in fields(actual_cls)
            if definition.init
            and definition.default is MISSING
            and definition.default_factory is MISSING
            and definition.name not in kwargs
        )
        if missing:
            raise ValueError({"expected_type": str(datacls), "missing": missing})
        return cast(T, actual_cls(**kwargs))


__all__ = ["ScaffoldDataclassFetcher"]
