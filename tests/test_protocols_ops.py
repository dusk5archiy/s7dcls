from __future__ import annotations

import unittest
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import Any

from s7dcls import (
    AllSwallower,
    AnySwallower,
    ChainFunction,
    ConstEmitter,
    DecoratedEmitter,
    DecoratedFunction,
    DefaultEmitter,
    FallbackEmitter,
    FallbackFunction,
    FirstMatchEmitter,
    FirstMatchFunction,
    IdentityTransform,
    KeyedFunction,
    NoopSwallower,
    SequenceTransform,
    StandardTypeDescriber,
    TappedEmitter,
    TappedFunction,
)


@dataclass
class _Node:
    label: str
    children: list[_Node]


type _RecursiveJson = None | int | str | list[_RecursiveJson]


class TestProtocolsPackage(unittest.TestCase):
    def test_transforms(self) -> None:
        identity = IdentityTransform[int]()
        self.assertEqual(identity(42), 42)

        seq = SequenceTransform[int](transforms=[lambda x: x + 1, lambda x: x * 3])
        self.assertEqual(seq(4), 15)
        self.assertEqual(SequenceTransform[str]()("keep"), "keep")

    def test_swallowers(self) -> None:
        seen: list[int] = []
        NoopSwallower[int]()(1)

        all_sw = AllSwallower[int](
            swallowers=[seen.append, lambda x: seen.append(x * 10)]
        )
        all_sw(2)
        self.assertEqual(seen, [2, 20])

        def _boom(x: int, /) -> None:
            raise ValueError(f"bad:{x}")

        any_sw = AnySwallower[int](
            swallowers=[_boom, seen.append],
            exceptions=(ValueError,),
        )
        any_sw(3)
        self.assertEqual(seen, [2, 20, 3])

        with self.assertRaises(RuntimeError) as err:
            AnySwallower[int](swallowers=[_boom], exceptions=(ValueError,))(4)
        self.assertIsInstance(err.exception.__cause__, ValueError)

        with self.assertRaises(ValueError):
            AnySwallower[int]()(5)

    def test_emitters(self) -> None:
        self.assertEqual(ConstEmitter(value="ok")(), "ok")

        first = FirstMatchEmitter[str](
            emitters=[
                ConstEmitter[str | None](value=None),
                ConstEmitter[str | None](value="hit"),
                ConstEmitter[str | None](value="later"),
            ]
        )
        self.assertEqual(first(), "hit")
        self.assertIsNone(FirstMatchEmitter[str]()())

        defaulted = DefaultEmitter[str](
            emitter=FirstMatchEmitter[str](
                emitters=[ConstEmitter[str | None](value=None)]
            ),
            default=ConstEmitter(value="fallback"),
        )
        self.assertEqual(defaulted(), "fallback")

        def _fail_emitter() -> str:
            raise OSError("offline")

        fb = FallbackEmitter[str](
            emitters=[_fail_emitter, ConstEmitter(value="mirror")],
            exceptions=(OSError,),
        )
        self.assertEqual(fb(), "mirror")

        with self.assertRaises(RuntimeError) as err:
            FallbackEmitter[str](emitters=[_fail_emitter], exceptions=(OSError,))()
        self.assertIsInstance(err.exception.__cause__, OSError)

        with self.assertRaises(ValueError):
            FallbackEmitter[str]()()

        dec = DecoratedEmitter[str](
            emitter=ConstEmitter(value="abc"),
            transform=str.upper,
        )
        self.assertEqual(dec(), "ABC")

        tapped_log: list[str] = []
        tapped = TappedEmitter[str](
            emitter=ConstEmitter(value="world.sdf"),
            swallower=tapped_log.append,
        )
        self.assertEqual(tapped(), "world.sdf")
        self.assertEqual(tapped_log, ["world.sdf"])

    def test_functions_and_chain(self) -> None:
        first_fn = FirstMatchFunction[int, str](
            functions=[
                lambda x: "even" if x % 2 == 0 else None,
                lambda x: "positive" if x > 0 else None,
            ]
        )
        self.assertEqual(first_fn(4), "even")
        self.assertEqual(first_fn(3), "positive")
        self.assertIsNone(first_fn(-3))

        def _fail_fn(x: int, /) -> str:
            raise ValueError(f"nope:{x}")

        fb_fn = FallbackFunction[int, str](
            functions=[_fail_fn, lambda x: f"ok:{x}"],
            exceptions=(ValueError,),
        )
        self.assertEqual(fb_fn(7), "ok:7")

        with self.assertRaises(RuntimeError) as err:
            FallbackFunction[int, str](functions=[_fail_fn], exceptions=(ValueError,))(
                8
            )
        self.assertIsInstance(err.exception.__cause__, ValueError)

        with self.assertRaises(ValueError):
            FallbackFunction[int, str]()(9)

        dec_fn = DecoratedFunction[int, str](
            function=lambda x: f"v{x}",
            transform=str.upper,
        )
        self.assertEqual(dec_fn(2), "V2")

        seen: list[str] = []
        tapped_fn = TappedFunction[int, str](
            function=lambda x: f"item-{x}",
            swallower=seen.append,
        )
        self.assertEqual(tapped_fn(5), "item-5")
        self.assertEqual(seen, ["item-5"])

        keyed = KeyedFunction[str, tuple[str, int], int](
            key_of=lambda pair: pair[0],
            handlers={
                "inc": lambda pair: pair[1] + 1,
                "dbl": lambda pair: pair[1] * 2,
            },
        )
        self.assertEqual(keyed(("inc", 3)), 4)
        self.assertEqual(keyed(("dbl", 3)), 6)
        with self.assertRaises(KeyError):
            keyed(("unknown", 3))

        keyed_default = KeyedFunction[str, tuple[str, int], int](
            key_of=lambda pair: pair[0],
            handlers={"inc": lambda pair: pair[1] + 1},
            default=lambda pair: pair[1],
        )
        self.assertEqual(keyed_default(("other", 9)), 9)

        chained = ChainFunction[str, int, bool](
            first=len,
            second=lambda n: n > 2,
        )
        self.assertTrue(chained("abc"))
        self.assertFalse(chained("ab"))

    def test_cycle_guarded_describer_without_contextvars_and_thread_safe(self) -> None:
        describer = StandardTypeDescriber.Args().build()

        def _describe_both(_: int) -> tuple[dict[str, Any], dict[str, Any]]:
            return describer(dtype=_Node), describer(dtype=_RecursiveJson)

        with ThreadPoolExecutor(max_workers=8) as pool:
            results = list(pool.map(_describe_both, range(32)))

        for node_schema, json_schema in results:
            fields_by_name = {f["name"]: f["schema"] for f in node_schema["fields"]}
            self.assertEqual(
                fields_by_name["children"],
                {"type": "array", "items": {"type": "dataclass_ref", "name": "_Node"}},
            )
            self.assertEqual(json_schema["type"], "union")
            self.assertIn(
                {
                    "type": "array",
                    "items": {"type": "alias_ref", "name": "_RecursiveJson"},
                },
                json_schema["variants"],
            )


if __name__ == "__main__":
    unittest.main()
