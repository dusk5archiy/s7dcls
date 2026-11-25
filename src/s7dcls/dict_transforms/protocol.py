from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from s7dcls.protocols import FunctionProtocol

DictTransformProtocol = FunctionProtocol[Mapping[str, Any], dict[str, Any]]


__all__ = ["DictTransformProtocol"]
