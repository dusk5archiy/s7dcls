from __future__ import annotations

from collections.abc import Mapping
from dataclasses import MISSING, dataclass, fields
from typing import TYPE_CHECKING, Any, cast

from s7dcls.dataclass_kwargs_resolvers.protocol import DataclassKwargsResolverProtocol
from s7dcls.error_paths import ErrorBatch
from s7dcls.type_hints import resolve_dataclass_type

from .protocol import DataclassHydratorProtocol

if TYPE_CHECKING:
    from _typeshed import DataclassInstance


@dataclass(kw_only=True, frozen=True)
class ScaffoldDataclassHydrator(DataclassHydratorProtocol):
    kwargs_resolver: DataclassKwargsResolverProtocol
    collect_errors: bool = False

    def __call__[T: DataclassInstance](
        self,
        *,
        data: Mapping[str, Any],
        datacls: type[T],
    ) -> T:
        resolved = resolve_dataclass_type(datacls)
        actual_cls = resolved[0] if resolved is not None else datacls
        batch = ErrorBatch(collect=self.collect_errors)
        kwargs: Mapping[str, Any] | None = None

        try:
            kwargs = self.kwargs_resolver(data=data, datacls=datacls)
        except (TypeError, ValueError, ExceptionGroup) as exc:
            batch.extend(exc=exc)

        if kwargs is not None:
            missing = sorted(
                definition.name
                for definition in fields(actual_cls)
                if definition.init
                and definition.default is MISSING
                and definition.default_factory is MISSING
                and definition.name not in kwargs
            )
        else:
            proj = getattr(self.kwargs_resolver, "class_key_projection", None)
            missing = []
            for definition in fields(actual_cls):
                if (
                    not definition.init
                    or definition.default is not MISSING
                    or definition.default_factory is not MISSING
                ):
                    continue
                alias = definition.metadata.get("alias")
                base_key = alias if isinstance(alias, str) else definition.name
                projected_key = proj(base_key) if callable(proj) else base_key
                if projected_key not in data:
                    missing.append(definition.name)
            missing.sort()

        if missing:
            batch.add(
                exc=ValueError({"expected_type": str(datacls), "missing": missing})
            )

        batch.raise_if_any()
        assert kwargs is not None
        return cast(T, actual_cls(**kwargs))


__all__ = ["ScaffoldDataclassHydrator"]
