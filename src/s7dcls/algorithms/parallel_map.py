from __future__ import annotations

from collections.abc import Sequence
from concurrent.futures import Future, ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field

from s7dcls.protocols.functions.protocol import FunctionProtocol
from s7dcls.protocols.swallowers.mechanism import NoopSwallower
from s7dcls.protocols.swallowers.protocol import SwallowerProtocol


@dataclass(kw_only=True, frozen=True)
class ParallelMapProgress[X, Y]:
    item: X
    result: Y
    done: int
    total: int


@dataclass(kw_only=True, frozen=True)
class ParallelMap[X, Y](FunctionProtocol[Sequence[X], list[Y]]):
    worker: FunctionProtocol[X, Y]
    max_summons: int = 4
    on_item_done: SwallowerProtocol[ParallelMapProgress[X, Y]] = field(
        default_factory=NoopSwallower[object]
    )

    def __post_init__(self) -> None:
        if self.max_summons < 1:
            raise ValueError({"max_summons": self.max_summons, "constraint": ">= 1"})

    def __call__(self, x: Sequence[X], /) -> list[Y]:
        total = len(x)
        if total == 0:
            return []

        summon_count = min(self.max_summons, total)
        results: dict[int, Y] = {}
        with ThreadPoolExecutor(max_workers=summon_count) as pool:
            future_to_entry: dict[Future[Y], tuple[int, X]] = {
                pool.submit(self.worker, item): (idx, item)
                for idx, item in enumerate(x)
            }
            done = 0
            try:
                for future in as_completed(future_to_entry):
                    idx, item = future_to_entry[future]
                    res = future.result()
                    results[idx] = res
                    done += 1
                    self.on_item_done(
                        ParallelMapProgress(
                            item=item,
                            result=res,
                            done=done,
                            total=total,
                        )
                    )
            except BaseException:
                for future in future_to_entry:
                    future.cancel()
                raise

        return [results[i] for i in range(total)]


__all__ = ["ParallelMap", "ParallelMapProgress"]
