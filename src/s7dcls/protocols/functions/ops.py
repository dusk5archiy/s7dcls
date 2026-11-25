from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from ..swallowers.protocol import SwallowerProtocol
from ..transforms.protocol import TransformProtocol
from .protocol import FunctionProtocol


@dataclass(kw_only=True, frozen=True)
class FirstMatchFunction[X, Y](FunctionProtocol[X, Y | None]):
    functions: Sequence[FunctionProtocol[X, Y | None]] = ()

    def __call__(self, x: X, /) -> Y | None:
        for function in self.functions:
            result = function(x)
            if result is not None:
                return result
        return None


@dataclass(kw_only=True, frozen=True)
class FallbackFunction[X, Y](FunctionProtocol[X, Y]):
    functions: Sequence[FunctionProtocol[X, Y]] = ()
    exceptions: tuple[type[Exception], ...] = (Exception,)

    def __call__(self, x: X, /) -> Y:
        errors: list[Exception] = []
        for function in self.functions:
            try:
                return function(x)
            except self.exceptions as exc:
                errors.append(exc)

        if errors:
            raise RuntimeError({"value": x, "errors": errors}) from errors[-1]
        raise ValueError({"value": x, "functions": ()})


@dataclass(kw_only=True, frozen=True)
class DecoratedFunction[X, Y](FunctionProtocol[X, Y]):
    function: FunctionProtocol[X, Y]
    transform: TransformProtocol[Y]

    def __call__(self, x: X, /) -> Y:
        return self.transform(self.function(x))


@dataclass(kw_only=True, frozen=True)
class TappedFunction[X, Y](FunctionProtocol[X, Y]):
    function: FunctionProtocol[X, Y]
    swallower: SwallowerProtocol[Y]

    def __call__(self, x: X, /) -> Y:
        result = self.function(x)
        self.swallower(result)
        return result


@dataclass(kw_only=True, frozen=True)
class KeyedFunction[K, X, Y](FunctionProtocol[X, Y]):
    key_of: FunctionProtocol[X, K]
    handlers: Mapping[K, FunctionProtocol[X, Y]]
    default: FunctionProtocol[X, Y] | None = None

    def __call__(self, x: X, /) -> Y:
        key = self.key_of(x)
        handler = self.handlers.get(key)
        if handler is not None:
            return handler(x)
        if self.default is not None:
            return self.default(x)
        raise KeyError({"key": key, "available": list(self.handlers)})


__all__ = [
    "DecoratedFunction",
    "FallbackFunction",
    "FirstMatchFunction",
    "KeyedFunction",
    "TappedFunction",
]
