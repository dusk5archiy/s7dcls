from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from s7dcls.type_emitters.protocol import EmitterProtocol

DictFetcherProtocol = EmitterProtocol[Mapping[str, Any]]


__all__ = ["DictFetcherProtocol"]
