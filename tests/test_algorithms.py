from __future__ import annotations

import threading
import time
import unittest
from collections.abc import Sequence

from s7dcls import BfsCrawler, ParallelMap, ParallelMapProgress


class TestAlgorithms(unittest.TestCase):
    def test_bfs_crawler_waves_cycles_and_deduplication(self) -> None:
        graph: dict[str, tuple[str, ...]] = {
            "a": ("b", "c"),
            "b": ("d", "a"),
            "c": ("d", "e"),
            "d": (),
            "e": ("b",),
        }
        waves: list[list[str]] = []

        def _resolve_nodes(batch: Sequence[str], /) -> dict[str, str]:
            waves.append(list(batch))
            return {node.lower(): node.lower() for node in batch}

        crawler = BfsCrawler[str, str, str](
            identify=str.lower,
            resolve_nodes=_resolve_nodes,
            discover=lambda val: graph[val],
        )

        resolved = crawler(["A", "a"])
        self.assertEqual(resolved, {"a": "a", "b": "b", "c": "c", "d": "d", "e": "e"})
        self.assertEqual(waves, [["A"], ["b", "c"], ["d", "e"]])

    def test_bfs_crawler_partial_resolution_does_not_revisit_omitted_nodes(
        self,
    ) -> None:
        attempts: list[str] = []

        def _resolve_nodes(batch: Sequence[str], /) -> dict[str, str]:
            attempts.extend(batch)
            return {node: node for node in batch if node != "missing"}

        graph: dict[str, tuple[str, ...]] = {
            "root": ("missing", "ok"),
            "ok": ("missing",),
        }
        crawler = BfsCrawler[str, str, str](
            identify=lambda x: x,
            resolve_nodes=_resolve_nodes,
            discover=lambda val: graph[val],
        )

        resolved = crawler(["root"])
        self.assertEqual(resolved, {"root": "root", "ok": "ok"})
        self.assertEqual(attempts.count("missing"), 1)

    def test_parallel_map_preserves_order_and_emits_progress(self) -> None:
        events: list[ParallelMapProgress[int, int]] = []
        callback_threads: set[int] = set()
        main_thread = threading.get_ident()

        def _worker(x: int, /) -> int:
            time.sleep((4 - x) * 0.005)
            return x * 10

        def _on_done(progress: ParallelMapProgress[int, int], /) -> None:
            callback_threads.add(threading.get_ident())
            events.append(progress)

        pmap = ParallelMap[int, int](
            worker=_worker,
            max_summons=4,
            on_item_done=_on_done,
        )

        self.assertEqual(pmap([]), [])
        out = pmap([1, 2, 3, 4])
        self.assertEqual(out, [10, 20, 30, 40])
        self.assertEqual(callback_threads, {main_thread})
        self.assertEqual([e.done for e in events], [1, 2, 3, 4])
        self.assertTrue(all(e.total == 4 for e in events))
        self.assertEqual(
            {e.item: e.result for e in events}, {1: 10, 2: 20, 3: 30, 4: 40}
        )

    def test_parallel_map_propagates_error_and_validates_max_summons(self) -> None:
        with self.assertRaises(ValueError):
            ParallelMap[int, int](worker=lambda x: x, max_summons=0)

        def _worker(x: int, /) -> int:
            if x == 2:
                raise RuntimeError("boom")
            return x

        pmap = ParallelMap[int, int](worker=_worker, max_summons=2)
        with self.assertRaisesRegex(RuntimeError, "boom"):
            pmap([1, 2, 3, 4])


if __name__ == "__main__":
    unittest.main()
