from __future__ import annotations

import tempfile
import unittest
from dataclasses import dataclass
from pathlib import Path
from typing import Annotated, Any, assert_type
from uuid import UUID

from s7dcls import (
    AllValueChecker,
    AnyValueChecker,
    CoerceResult,
    DescribeTypeResult,
    ErrorPath,
    FallbackCoercer,
    FirstMatchCoercerWorker,
    FirstMatchFileDictLoaderWorker,
    FirstMatchTypeDescriberWorker,
    FirstMatchUncoercerWorker,
    FirstMatchValidatorWorker,
    Ge,
    Gt,
    HubCoercer,
    HubTypeDescriber,
    HubUncoercer,
    HubValidator,
    JsonFileDictLoaderWorker,
    Le,
    Lt,
    ScaffoldFileDictLoader,
    StandardDataclassDehydrator,
    StandardDataclassHydrator,
    StandardJsonCoercer,
    StandardStringCoercer,
    StandardTypeDescriber,
    StandardUncoercer,
    StandardValidator,
    TomlFileDictLoaderWorker,
    UncoerceResult,
    ValidateResult,
    validate,
)
from s7dcls.coercers.mechanism import (
    AnyCoercerWorker,
    ListCoercerWorker,
    TypeInstanceCoercerWorker,
)
from s7dcls.type_describers.mechanism import (
    ListTypeDescriberWorker,
    TypeInstanceDescriberWorker,
)
from s7dcls.uncoercers.mechanism import (
    PrimitiveUncoercerWorker,
    SequenceUncoercerWorker,
)
from s7dcls.validators.mechanism import ListValidatorWorker, TypeInstanceValidatorWorker


@dataclass(kw_only=True, frozen=True)
class _PathLeaf:
    port: Annotated[int, Gt(limit=0)]


@dataclass(kw_only=True, frozen=True)
class _PathGroup:
    items: tuple[_PathLeaf, ...]


@dataclass(kw_only=True, frozen=True)
class _PathRoot:
    groups: dict[str, list[_PathGroup]]


@validate
@dataclass(kw_only=True, frozen=True)
class _CheckedRoot:
    items: list[_PathLeaf]


@dataclass(kw_only=True, frozen=True)
class _BadDehydrate:
    entries: dict[str, list[Any]]


class TestOpsAndScaffolds(unittest.TestCase):
    def test_any_coercer_and_standard_json_vs_string_separation(self) -> None:
        any_coercer = AnyCoercerWorker()
        self.assertEqual(
            any_coercer(value={"k": 1}, dtype=Any), CoerceResult(value={"k": 1})
        )
        self.assertIsNone(any_coercer(value=1, dtype=int))

        json_coercer = StandardJsonCoercer.Args().build()
        string_coercer = StandardStringCoercer.Args().build()

        self.assertTrue(json_coercer.can_handle(dtype=list[int]))
        self.assertFalse(json_coercer.can_handle(dtype=int))
        self.assertFalse(hasattr(string_coercer, "can_handle"))

        self.assertEqual(json_coercer(value=42, dtype=Any), 42)
        self.assertEqual(string_coercer(value="[1, 2]", dtype=list[int]), [1, 2])
        self.assertEqual(string_coercer(value="true", dtype=bool), True)

        as_tuple = json_coercer(value=[1, 2], dtype=tuple[int, ...])
        assert_type(as_tuple, tuple[int, ...])
        self.assertEqual(as_tuple, (1, 2))

        as_int = string_coercer(value="42", dtype=int)
        assert_type(as_int, int)
        self.assertEqual(as_int, 42)

        as_path = json_coercer(value="/tmp/x", dtype=Path)
        assert_type(as_path, Path)
        self.assertEqual(as_path, Path("/tmp/x"))

        as_union = string_coercer(value="null", dtype=int | None)
        self.assertIsNone(as_union)

    def test_scaffold_coercer_supports_custom_recursive_type(self) -> None:
        @dataclass(kw_only=True, frozen=True)
        class UuidCoercerWorker:
            def __call__(self, *, value: Any, dtype: Any) -> CoerceResult[UUID] | None:
                if dtype is not UUID:
                    return None
                if isinstance(value, UUID):
                    return CoerceResult(value=value)
                if isinstance(value, str):
                    return CoerceResult(value=UUID(value))
                raise TypeError({"value": value, "expected_type": str(UUID)})

        coercer = HubCoercer.Args(
            spawner=lambda hub: FirstMatchCoercerWorker(
                workers=(
                    ListCoercerWorker(hub=hub),
                    UuidCoercerWorker(),
                    TypeInstanceCoercerWorker(datatype=int),
                )
            )
        ).build()

        raw = "12345678-1234-5678-1234-567812345678"
        self.assertEqual(coercer(value=[raw], dtype=list[UUID]), [UUID(raw)])
        with self.assertRaises(TypeError):
            coercer(value="x", dtype=str)

    def test_first_match_coercer_stops_on_committed_error(self) -> None:
        first_match = FirstMatchCoercerWorker(
            workers=(
                TypeInstanceCoercerWorker(datatype=int),
                AnyCoercerWorker(),
            )
        )
        with self.assertRaises(TypeError):
            first_match(value="42", dtype=int)

    def test_fallback_coercer_recovers_from_error_across_strict_coercers(self) -> None:
        fallback = FallbackCoercer(
            coercers=(
                StandardJsonCoercer.Args().build(),
                StandardStringCoercer.Args().build(),
            )
        )
        self.assertEqual(fallback(value=123, dtype=int), 123)
        self.assertEqual(fallback(value="123", dtype=int), 123)
        with self.assertRaises(ValueError):
            fallback(value="not-an-int", dtype=int)

    def test_scaffold_and_first_match_uncoercer(self) -> None:
        @dataclass(kw_only=True, frozen=True)
        class UuidUncoercerWorker:
            def __call__(self, *, value: Any) -> UncoerceResult | None:
                if isinstance(value, UUID):
                    return UncoerceResult(value=str(value))
                return None

        uncoercer = HubUncoercer.Args(
            spawner=lambda hub: FirstMatchUncoercerWorker(
                workers=(
                    UuidUncoercerWorker(),
                    PrimitiveUncoercerWorker(),
                    SequenceUncoercerWorker(hub=hub),
                )
            )
        ).build()
        uid = UUID("12345678-1234-5678-1234-567812345678")
        self.assertEqual(uncoercer(value=[uid, 1]), [str(uid), 1])
        self.assertEqual(StandardUncoercer()(value=Path("/tmp")), "/tmp")

    def test_scaffold_and_first_match_validator(self) -> None:
        @dataclass(kw_only=True, frozen=True)
        class UuidValidatorWorker:
            def __call__(self, *, value: Any, dtype: Any) -> ValidateResult | None:
                if dtype is not UUID:
                    return None
                if not isinstance(value, UUID):
                    raise TypeError({"value": value, "expected_type": str(UUID)})
                return ValidateResult()

        validator = HubValidator.Args(
            spawner=lambda hub: FirstMatchValidatorWorker(
                workers=(
                    ListValidatorWorker(hub=hub),
                    UuidValidatorWorker(),
                    TypeInstanceValidatorWorker(datatype=int),
                )
            )
        ).build()
        uid = UUID("12345678-1234-5678-1234-567812345678")
        validator(value=[uid], dtype=list[UUID])
        with self.assertRaises(TypeError):
            validator(value=["bad"], dtype=list[UUID])

    def test_scaffold_and_first_match_type_describer(self) -> None:
        @dataclass(kw_only=True, frozen=True)
        class UuidDescriberWorker:
            def __call__(self, *, dtype: Any) -> DescribeTypeResult | None:
                if dtype is not UUID:
                    return None
                return DescribeTypeResult(schema={"type": "uuid"})

        describer = HubTypeDescriber(
            spawner=lambda hub: FirstMatchTypeDescriberWorker(
                workers=(
                    ListTypeDescriberWorker(hub=hub),
                    UuidDescriberWorker(),
                    TypeInstanceDescriberWorker(datatype=int, type_name="int"),
                )
            )
        )
        self.assertEqual(
            describer(dtype=list[UUID]),
            {"type": "array", "items": {"type": "uuid"}},
        )
        self.assertEqual(
            StandardTypeDescriber.Args().build()(dtype=int),
            {"type": "int"},
        )

    def test_file_dict_loader_ops_and_scaffold(self) -> None:
        worker = FirstMatchFileDictLoaderWorker(
            workers=(JsonFileDictLoaderWorker(), TomlFileDictLoaderWorker())
        )
        self.assertIsNone(worker(Path("/nonexistent/config.yaml")))
        loader = ScaffoldFileDictLoader(worker=worker)
        with tempfile.TemporaryDirectory() as tmp:
            fp = Path(tmp) / "a.json"
            fp.write_text('{"x": 1}', encoding="utf-8")
            self.assertEqual(loader(fp), {"x": 1})
        with self.assertRaises(ValueError):
            loader(Path("/nonexistent/config.yaml"))

    def test_value_checker_all_and_any_ops(self) -> None:
        in_range = AllValueChecker(checkers=(Ge(limit=1), Le(limit=10)))
        in_range(1)
        in_range(10)
        with self.assertRaises(ValueError):
            in_range(0)

        zero_or_gt_10 = AnyValueChecker(
            checkers=(
                AllValueChecker(checkers=(Ge(limit=0), Le(limit=0))),
                Gt(limit=10),
            )
        )
        zero_or_gt_10(0)
        zero_or_gt_10(11)
        with self.assertRaises(ValueError):
            zero_or_gt_10(5)

        coercer = StandardJsonCoercer.Args().build()
        validator = StandardValidator.Args().build()
        dtype = Annotated[int, AnyValueChecker(checkers=(Lt(limit=0), Gt(limit=10)))]
        self.assertEqual(coercer(value=-5, dtype=dtype), -5)
        self.assertEqual(coercer(value=20, dtype=dtype), 20)
        validator(value=-5, dtype=dtype)
        with self.assertRaises(ValueError):
            coercer(value=5, dtype=dtype)
        with self.assertRaises(ValueError):
            validator(value=5, dtype=dtype)

    def test_nested_error_paths_across_coercer_validator_and_dehydrator(self) -> None:
        hydrator = StandardDataclassHydrator.Args().build()
        with self.assertRaises(ValueError) as ctx:
            hydrator(
                data={
                    "groups": {
                        "alpha": [
                            {"items": [{"port": 80}, {"port": 0}]},
                        ]
                    }
                },
                datacls=_PathRoot,
            )
        self.assertEqual(
            ctx.exception.args[0]["path"],
            ("groups", "alpha", 0, "items", 1, "port"),
        )
        self.assertEqual(ctx.exception.args[0]["value"], 0)
        self.assertEqual(ctx.exception.args[0]["constraint"], "> 0")

        bad_root = _PathRoot(
            groups={
                "alpha": [_PathGroup(items=(_PathLeaf(port=80), _PathLeaf(port=-3)))]
            }
        )
        validator = StandardValidator.Args().build()
        with self.assertRaises(ValueError) as vctx:
            validator(value=bad_root, dtype=_PathRoot)
        self.assertEqual(
            vctx.exception.args[0]["path"],
            ("groups", "alpha", 0, "items", 1, "port"),
        )

        with self.assertRaises(ValueError) as dctx:
            _CheckedRoot(items=[_PathLeaf(port=1), _PathLeaf(port=0)])
        self.assertEqual(dctx.exception.args[0]["path"], ("items", 1, "port"))

        class Unsupported:
            pass

        dehydrator = StandardDataclassDehydrator.Args().build()
        with self.assertRaises(TypeError) as uctx:
            dehydrator(instance=_BadDehydrate(entries={"k": [1, Unsupported()]}))
        self.assertEqual(uctx.exception.args[0]["path"], ("entries", "k", 1))

        reusable = ErrorPath(segment=True)
        for _ in range(2):
            with self.assertRaises(ValueError) as rctx, reusable:
                raise ValueError({"value": 1})
            self.assertEqual(rctx.exception.args[0]["path"], ("True",))
        err = ValueError({"value": 1, "path": ("True",)})
        ErrorPath.prepend(exc=err, segment="outer")
        self.assertEqual(err.args[0]["path"], ("outer", "True"))


if __name__ == "__main__":
    unittest.main()
