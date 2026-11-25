from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass

from s7dcls.protocols.functions.protocol import FunctionProtocol


@dataclass(kw_only=True, frozen=True)
class BfsCrawler[K, Node, V](FunctionProtocol[Iterable[Node], dict[K, V]]):
    identify: FunctionProtocol[Node, K]
    resolve_nodes: FunctionProtocol[Sequence[Node], Mapping[K, V]]
    discover: FunctionProtocol[V, Iterable[Node]]

    def __call__(self, x: Iterable[Node], /) -> dict[K, V]:
        resolved: dict[K, V] = {}
        seen: set[K] = set()
        frontier: dict[K, Node] = {}

        for node in x:
            key = self.identify(node)
            if key not in seen:
                seen.add(key)
                frontier[key] = node

        while frontier:
            current_keys = tuple(frontier)
            current_resolved = self.resolve_nodes(list(frontier.values()))
            frontier = {}
            resolved.update(current_resolved)
            for value in (
                current_resolved[k] for k in current_keys if k in current_resolved
            ):
                for node in self.discover(value):
                    key = self.identify(node)
                    if key not in seen:
                        seen.add(key)
                        frontier[key] = node

        return resolved


__all__ = ["BfsCrawler"]
