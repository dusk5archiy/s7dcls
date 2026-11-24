from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from s7dcls.string_manipulations.string_gates.protocol import StringGateProtocol

from .protocol import DictTransformProtocol


@dataclass(kw_only=True, frozen=True)
class KeyGateDictTransform(DictTransformProtocol):
    key_gate: StringGateProtocol

    def __call__(self, x: Mapping[str, Any]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for data_key, data_value in x.items():
            _gated = self.key_gate(data_key)
            if _gated is not None:
                result[_gated] = data_value
        return result


@dataclass(kw_only=True, frozen=True)
class KeyPathDictTransform(DictTransformProtocol):
    key_path: Sequence[str]

    def __call__(self, x: Mapping[str, Any]) -> dict[str, Any]:
        current: Any = x
        traversed: list[str] = []
        for segment in self.key_path:
            traversed.append(segment)
            if not isinstance(current, Mapping):
                raise ValueError(  # noqa: TRY004
                    {
                        "key_path": tuple(traversed[:-1]),
                        "expected_type": str(Mapping[str, Any]),
                        "got_type": str(type(current)),
                    }
                )
            if segment not in current:
                return {}
            current = current[segment]

        if not isinstance(current, Mapping) or not all(
            isinstance(k, str) for k in current
        ):
            raise ValueError(
                {
                    "key_path": tuple(traversed),
                    "expected_type": str(Mapping[str, Any]),
                    "got_type": str(type(current)),
                }
            )
        return dict(current)


__all__ = ["KeyGateDictTransform", "KeyPathDictTransform"]
