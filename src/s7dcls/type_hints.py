from __future__ import annotations

from collections.abc import Mapping
from functools import lru_cache
from types import MappingProxyType
from typing import Any, get_type_hints


@lru_cache(maxsize=512)
def get_cached_type_hints(cls: type[Any]) -> Mapping[str, Any]:
    return MappingProxyType(get_type_hints(cls, include_extras=True))


__all__ = ["get_cached_type_hints"]
