from __future__ import annotations

import unittest
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from decimal import Decimal
from enum import IntEnum, StrEnum
from typing import Annotated, Literal
from uuid import UUID

from s7dcls import (
    JSON_SCHEMA_DRAFT_2020_12,
    ChainSchemaDescriber,
    DecoratedSchemaDescriber,
    Gt,
    JsonSchemaDictTransform,
    MaxLen,
    MinLen,
    MultipleOf,
    NonEmptyStr,
    ScaffoldDataclassFetcher,
    StandardDataclassDehydrator,
    StandardDataclassHydrator,
    StandardJsonCoercer,
    StandardJsonSchemaDescriber,
    StandardStringCoercer,
    StandardTypeDescriber,
    StandardUncoercer,
    StandardValidator,
    UniqueItems,
    resolve_dataclass_type,
    resolve_tagged_union,
)


class _Mode(StrEnum):
    FAST = "fast"
    SAFE = "safe"


class _Level(IntEnum):
    LOW = 1
    HIGH = 2


@dataclass(kw_only=True, frozen=True)
class _RequiredItem:
    host: str
    port: int


@dataclass(kw_only=True, frozen=True)
class _RequiredContainer:
    groups: dict[str, list[_RequiredItem]]


@dataclass(kw_only=True, frozen=True)
class _RichRecord:
    uid: UUID
    created_at: datetime
    day: date
    timeout: timedelta
    amount: Decimal
    mode: _Mode
    level: _Level
    tags: set[str]
    frozen_ids: frozenset[int]


type _PortAlias = Annotated[int, Gt(limit=0)]


@dataclass(kw_only=True, frozen=True)
class _TreeNode:
    name: str
    children: list[_TreeNode] = field(default_factory=list)


@dataclass(kw_only=True, frozen=True)
class _User:
    name: Annotated[str, NonEmptyStr()]
    age: Annotated[int, Gt(limit=0)]


@dataclass(kw_only=True, frozen=True)
class _Page[T]:
    items: list[T]
    total: int


@dataclass(kw_only=True, frozen=True)
class _Cat:
    kind: Literal["cat"]
    lives: Annotated[int, Gt(limit=0)]


@dataclass(kw_only=True, frozen=True)
class _Dog:
    kind: Literal["dog"]
    bark_db: Annotated[int, Gt(limit=0)]


@dataclass(kw_only=True, frozen=True)
class _AmbiguousA:
    kind: Literal["a"]
    group: Literal[1]


@dataclass(kw_only=True, frozen=True)
class _AmbiguousB:
    kind: Literal["b"]
    group: Literal[2]


type _Pet = _Cat | _Dog


@dataclass(kw_only=True, frozen=True)
class _MultiErrorForm:
    host: Annotated[str, NonEmptyStr()]
    port: Annotated[int, Gt(limit=0)]
    tag: int | str
    users: list[_User]
    required_token: str


@dataclass(kw_only=True, frozen=True)
class _Order:
    order_id: str


@dataclass(kw_only=True, frozen=True)
class _Dashboard:
    users_page: _Page[_User]
    orders_page: _Page[_Order]


@dataclass(kw_only=True, frozen=True)
class _AliasedPayload:
    from_: Annotated[str, NonEmptyStr()] = field(metadata={"alias": "from"})
    ref: str = field(metadata={"alias": "$ref"})
    body: str = ""


class TestExtensions(unittest.TestCase):
    def test_missing_required_fields_structured_error_and_nested_path(self) -> None:
        hydrator = StandardDataclassHydrator.Args().build()
        with self.assertRaises(ValueError) as root_ctx:
            hydrator(data={"host": "localhost"}, datacls=_RequiredItem)
        self.assertEqual(root_ctx.exception.args[0]["missing"], ["port"])

        with self.assertRaises(ValueError) as nested_ctx:
            hydrator(
                data={"groups": {"alpha": [{"host": "127.0.0.1"}]}},
                datacls=_RequiredContainer,
            )
        self.assertEqual(nested_ctx.exception.args[0]["missing"], ["port"])
        self.assertEqual(nested_ctx.exception.args[0]["path"], ("groups", "alpha", 0))

        fetcher = ScaffoldDataclassFetcher(source=lambda *, datacls: {"port": 80})
        with self.assertRaises(ValueError) as fetch_ctx:
            fetcher(datacls=_RequiredItem)
        self.assertEqual(fetch_ctx.exception.args[0]["missing"], ["host"])

    def test_enum_set_uuid_datetime_decimal_roundtrip_and_strictness(self) -> None:
        uid = UUID("12345678-1234-5678-1234-567812345678")
        dt = datetime(2026, 11, 25, 16, 30, 0)
        d = date(2026, 11, 25)
        td = timedelta(seconds=12.5)
        dec = Decimal("19.95")

        raw = {
            "uid": str(uid),
            "created_at": dt.isoformat(),
            "day": d.isoformat(),
            "timeout": 12.5,
            "amount": "19.95",
            "mode": "fast",
            "level": 2,
            "tags": ["a", "b"],
            "frozen_ids": [1, 2],
        }
        hydrator = StandardDataclassHydrator.Args().build()
        dehydrator = StandardDataclassDehydrator.Args().build()
        validator = StandardValidator.Args().build()

        rec = hydrator(data=raw, datacls=_RichRecord)
        self.assertEqual(rec.uid, uid)
        self.assertEqual(rec.created_at, dt)
        self.assertEqual(rec.day, d)
        self.assertEqual(rec.timeout, td)
        self.assertEqual(rec.amount, dec)
        self.assertIs(rec.mode, _Mode.FAST)
        self.assertIs(rec.level, _Level.HIGH)
        self.assertEqual(rec.tags, {"a", "b"})
        self.assertEqual(rec.frozen_ids, frozenset({1, 2}))

        validator(value=rec, dtype=_RichRecord)

        out = dehydrator(instance=rec)
        self.assertEqual(out["uid"], str(uid))
        self.assertEqual(out["created_at"], dt.isoformat())
        self.assertEqual(out["day"], d.isoformat())
        self.assertEqual(out["timeout"], 12.5)
        self.assertEqual(out["amount"], "19.95")
        self.assertIs(type(out["mode"]), str)
        self.assertEqual(out["mode"], "fast")
        self.assertIs(type(out["level"]), int)
        self.assertEqual(out["level"], 2)
        self.assertEqual(set(out["tags"]), {"a", "b"})
        self.assertEqual(set(out["frozen_ids"]), {1, 2})

        json_coercer = StandardJsonCoercer.Args().build()
        with self.assertRaises(ValueError):
            json_coercer(value=True, dtype=_Level)
        with self.assertRaises(ValueError):
            json_coercer(value="1", dtype=_Level)
        with self.assertRaises(TypeError):
            json_coercer(value=dt, dtype=date)
        with self.assertRaises(TypeError):
            validator(value=dt, dtype=date)
        with self.assertRaises(TypeError):
            json_coercer(value=True, dtype=timedelta)
        with self.assertRaises(TypeError):
            json_coercer(value=True, dtype=Decimal)
        with self.assertRaises(TypeError) as set_err:
            json_coercer(value=[1, "bad"], dtype=set[int])
        self.assertEqual(set_err.exception.args[0]["path"], (1,))

        str_coercer = StandardStringCoercer.Args().build()
        self.assertIs(str_coercer(value="2", dtype=_Level), _Level.HIGH)
        self.assertIs(str_coercer(value="safe", dtype=_Mode), _Mode.SAFE)
        self.assertEqual(str_coercer(value=str(uid), dtype=UUID), uid)
        self.assertEqual(
            str_coercer(value="2.5", dtype=timedelta), timedelta(seconds=2.5)
        )
        self.assertEqual(str_coercer(value="10.25", dtype=Decimal), Decimal("10.25"))
        self.assertEqual(
            str_coercer(value='["x", "y"]', dtype=frozenset[str]),
            frozenset({"x", "y"}),
        )

        uncoercer = StandardUncoercer.Args().build()
        self.assertEqual(uncoercer(value=_Mode.FAST), "fast")
        self.assertIs(type(uncoercer(value=_Mode.FAST)), str)

        self.assertEqual(json_coercer(value=80, dtype=_PortAlias), 80)
        validator(value=80, dtype=_PortAlias)
        with self.assertRaises(ValueError):
            json_coercer(value=0, dtype=_PortAlias)

    def test_new_value_checkers_and_self_referential_describer(self) -> None:
        coercer = StandardJsonCoercer.Args().build()
        describer = StandardTypeDescriber.Args().build()

        tags_type = Annotated[
            list[str], MinLen(limit=1), MaxLen(limit=3), UniqueItems()
        ]
        self.assertEqual(coercer(value=["a", "b"], dtype=tags_type), ["a", "b"])
        with self.assertRaises(ValueError):
            coercer(value=[], dtype=tags_type)
        with self.assertRaises(ValueError):
            coercer(value=["a", "b", "c", "d"], dtype=tags_type)
        with self.assertRaises(ValueError):
            coercer(value=["a", "a"], dtype=tags_type)

        UniqueItems()([1, True])

        step_type = Annotated[float, MultipleOf(step=0.1)]
        self.assertEqual(coercer(value=0.3, dtype=step_type), 0.3)
        with self.assertRaises(ValueError):
            coercer(value=0.35, dtype=step_type)
        with self.assertRaises(ValueError):
            MultipleOf(step=0)

        tags_schema = describer(dtype=tags_type)
        self.assertEqual(tags_schema["min_length"], 1)
        self.assertEqual(tags_schema["max_length"], 3)
        self.assertTrue(tags_schema["unique_items"])

        step_schema = describer(dtype=step_type)
        self.assertEqual(step_schema["multiple_of"], 0.1)

        rich_schema = describer(dtype=_RichRecord)
        fields_by_name = {f["name"]: f["schema"] for f in rich_schema["fields"]}
        self.assertEqual(fields_by_name["uid"], {"type": "uuid"})
        self.assertEqual(fields_by_name["created_at"], {"type": "datetime"})
        self.assertEqual(fields_by_name["day"], {"type": "date"})
        self.assertEqual(fields_by_name["timeout"], {"type": "timedelta"})
        self.assertEqual(fields_by_name["amount"], {"type": "decimal"})
        self.assertEqual(
            fields_by_name["mode"],
            {"type": "enum", "name": "_Mode", "choices": ["fast", "safe"]},
        )
        self.assertEqual(
            fields_by_name["tags"],
            {"type": "array", "items": {"type": "str"}, "unique": True},
        )

        tree_schema = describer(dtype=_TreeNode)
        tree_fields = {f["name"]: f["schema"] for f in tree_schema["fields"]}
        self.assertEqual(
            tree_fields["children"],
            {"type": "array", "items": {"type": "dataclass_ref", "name": "_TreeNode"}},
        )

    def test_generic_dataclass_coercer_validator_and_describer(self) -> None:
        hydrator = StandardDataclassHydrator.Args().build()
        validator = StandardValidator.Args().build()
        describer = StandardTypeDescriber.Args().build()

        page = hydrator(
            data={
                "items": [{"name": "Ada", "age": 36}, {"name": "Grace", "age": 85}],
                "total": 2,
            },
            datacls=_Page[_User],
        )
        self.assertEqual(page.total, 2)
        self.assertEqual(
            page.items, [_User(name="Ada", age=36), _User(name="Grace", age=85)]
        )
        validator(value=page, dtype=_Page[_User])

        with self.assertRaises(ValueError) as err:
            hydrator(
                data={"items": [{"name": "Ada", "age": 0}], "total": 1},
                datacls=_Page[_User],
            )
        self.assertEqual(err.exception.args[0]["path"], ("items", 0, "age"))

        bad_page = _Page(items=[_User(name="Ada", age=-1)], total=1)
        with self.assertRaises(ValueError) as verr:
            validator(value=bad_page, dtype=_Page[_User])
        self.assertEqual(verr.exception.args[0]["path"], ("items", 0, "age"))

        schema = describer(dtype=_Page[_User])
        fields_by_name = {f["name"]: f["schema"] for f in schema["fields"]}
        self.assertEqual(fields_by_name["items"]["items"]["name"], "_User")
        res_a = resolve_dataclass_type(_Page[_User])
        res_b = resolve_dataclass_type(_Page[_User])
        self.assertIsNotNone(res_a)
        self.assertIs(res_a, res_b)

    def test_json_schema_dict_transform_and_decorated_describer(self) -> None:
        js = StandardJsonSchemaDescriber.Args().build()
        chained = ChainSchemaDescriber(
            type_describer=StandardTypeDescriber.Args().build(),
            dict_transform=JsonSchemaDictTransform(),
        )
        self.assertEqual(js(dtype=_Page[_User]), chained(dtype=_Page[_User]))

        decorated = DecoratedSchemaDescriber(
            schema_describer=js,
            dict_transform=lambda s: {**s, "$id": "https://example.test/page"},
        )
        self.assertEqual(
            decorated(dtype=_Page[_User])["$id"], "https://example.test/page"
        )

        page_schema = js(dtype=_Page[_User])
        self.assertEqual(page_schema["$schema"], JSON_SCHEMA_DRAFT_2020_12)
        self.assertEqual(page_schema["type"], "object")
        self.assertEqual(page_schema["title"], "_Page[_User]")
        self.assertEqual(page_schema["required"], ["items", "total"])
        self.assertEqual(
            page_schema["properties"]["items"],
            {"type": "array", "items": {"$ref": "#/$defs/_User"}},
        )
        user_def = page_schema["$defs"]["_User"]
        self.assertEqual(user_def["properties"]["name"]["minLength"], 1)
        self.assertEqual(user_def["properties"]["age"]["exclusiveMinimum"], 0)

        tree_schema = js(dtype=_TreeNode)
        self.assertEqual(
            tree_schema["properties"]["children"],
            {"type": "array", "items": {"$ref": "#"}},
        )
        self.assertEqual(tree_schema["required"], ["name"])

        tuple_schema = js(dtype=tuple[int, str])
        self.assertEqual(
            tuple_schema["prefixItems"],
            [{"type": "integer"}, {"type": "string"}],
        )
        self.assertEqual(tuple_schema["minItems"], 2)
        self.assertEqual(tuple_schema["maxItems"], 2)

        opt_schema = js(dtype=int | None)
        self.assertEqual(
            opt_schema["anyOf"],
            [{"type": "integer"}, {"type": "null"}],
        )

    def test_auto_tagged_union_worker_coercer_and_validator(self) -> None:
        coercer = StandardJsonCoercer.Args().build()
        str_coercer = StandardStringCoercer.Args().build()
        validator = StandardValidator.Args().build()

        # Auto-detected O(1) tagged union on plain Python union (no metadata!)
        spec_a = resolve_tagged_union(_Cat | _Dog)
        spec_b = resolve_tagged_union(_Cat | _Dog)
        self.assertIsNotNone(spec_a)
        self.assertIs(spec_a, spec_b)
        assert spec_a is not None
        self.assertEqual(spec_a.field, "kind")

        cat = coercer(value={"kind": "cat", "lives": 9}, dtype=_Pet)
        self.assertEqual(cat, _Cat(kind="cat", lives=9))
        validator(value=cat, dtype=_Pet)

        # String coercer parses JSON string for tagged union automatically
        dog = str_coercer(value='{"kind": "dog", "bark_db": 80}', dtype=_Pet)
        self.assertEqual(dog, _Dog(kind="dog", bark_db=80))

        # Direct inner ErrorPath preserved (not wrapped in generic Union errors)
        with self.assertRaises(ValueError) as inner_err:
            coercer(value={"kind": "cat", "lives": 0}, dtype=_Pet)
        self.assertEqual(inner_err.exception.args[0]["path"], ("lives",))
        self.assertEqual(inner_err.exception.args[0]["constraint"], "> 0")

        with self.assertRaises(ValueError) as missing_tag:
            coercer(value={"lives": 9}, dtype=_Pet)
        self.assertEqual(missing_tag.exception.args[0]["missing"], ["kind"])

        with self.assertRaises(ValueError) as bad_tag:
            coercer(value={"kind": "bird", "lives": 9}, dtype=_Pet)
        self.assertEqual(bad_tag.exception.args[0]["path"], ("kind",))
        self.assertEqual(bad_tag.exception.args[0]["allowed"], ["cat", "dog"])

        with self.assertRaises(ValueError) as val_err:
            validator(value=_Dog(kind="dog", bark_db=0), dtype=_Pet)
        self.assertEqual(val_err.exception.args[0]["path"], ("bark_db",))

        # Optional tagged union
        opt_pet = _Cat | _Dog | None
        self.assertIsNone(coercer(value=None, dtype=opt_pet))
        validator(value=None, dtype=opt_pet)
        self.assertEqual(
            coercer(value={"kind": "dog", "bark_db": 50}, dtype=opt_pet),
            _Dog(kind="dog", bark_db=50),
        )

        # Ambiguous (>= 2 disjoint literal fields) falls back cleanly to UnionWorker
        self.assertIsNone(resolve_tagged_union(_AmbiguousA | _AmbiguousB))
        self.assertEqual(
            coercer(value={"kind": "a", "group": 1}, dtype=_AmbiguousA | _AmbiguousB),
            _AmbiguousA(kind="a", group=1),
        )

    def test_explicit_collect_errors_bottom_up_exception_group(self) -> None:
        hydrator = StandardDataclassHydrator.Args(collect_errors=True).build()
        validator = StandardValidator.Args(collect_errors=True).build()

        with self.assertRaises(ExceptionGroup) as ctx:
            hydrator(
                data={
                    "host": "",
                    "port": -5,
                    "tag": "ok",
                    "users": [
                        {"name": "", "age": 0},
                        {"name": "Bob", "age": "not-int"},
                    ],
                    "extra_key": 123,
                },
                datacls=_MultiErrorForm,
            )

        payloads = [exc.args[0] for exc in ctx.exception.exceptions]
        paths = [p.get("path", ()) for p in payloads]
        self.assertIn(("host",), paths)
        self.assertIn(("port",), paths)
        self.assertIn(("users", 0, "name"), paths)
        self.assertIn(("users", 0, "age"), paths)
        self.assertIn(("users", 1, "age"), paths)
        self.assertTrue(any(p.get("unknown") == ["extra_key"] for p in payloads))
        self.assertTrue(any(p.get("missing") == ["required_token"] for p in payloads))
        # Valid union field ("tag": "ok") must NOT leak spurious int-branch error
        self.assertNotIn(("tag",), paths)
        # Flattened: no nested ExceptionGroups
        self.assertFalse(
            any(isinstance(e, ExceptionGroup) for e in ctx.exception.exceptions)
        )

        bad_form = _MultiErrorForm(
            host="",
            port=0,
            tag="ok",
            users=[_User(name="", age=-1)],
            required_token="tok",
        )
        with self.assertRaises(ExceptionGroup) as vctx:
            validator(value=bad_form, dtype=_MultiErrorForm)
        vpaths = [exc.args[0].get("path") for exc in vctx.exception.exceptions]
        self.assertEqual(
            vpaths,
            [("host",), ("port",), ("users", 0, "name"), ("users", 0, "age")],
        )

        # Default (collect_errors=False) stays fail-fast single exception
        fast_hydrator = StandardDataclassHydrator.Args().build()
        with self.assertRaises(ValueError) as fast_ctx:
            fast_hydrator(
                data={"host": "", "port": -5, "tag": "ok", "users": []},
                datacls=_MultiErrorForm,
            )
        self.assertNotIsInstance(fast_ctx.exception, ExceptionGroup)

    def test_generic_defs_collision_free_and_field_alias_roundtrip(self) -> None:
        js = StandardJsonSchemaDescriber.Args().build()
        dash = js(dtype=_Dashboard)
        self.assertEqual(
            dash["properties"]["users_page"], {"$ref": "#/$defs/_Page[_User]"}
        )
        self.assertEqual(
            dash["properties"]["orders_page"], {"$ref": "#/$defs/_Page[_Order]"}
        )
        self.assertIn("_Page[_User]", dash["$defs"])
        self.assertIn("_Page[_Order]", dash["$defs"])
        self.assertEqual(
            dash["$defs"]["_Page[_User]"]["properties"]["items"]["items"],
            {"$ref": "#/$defs/_User"},
        )
        self.assertEqual(
            dash["$defs"]["_Page[_Order]"]["properties"]["items"]["items"],
            {"$ref": "#/$defs/_Order"},
        )

        hydrator = StandardDataclassHydrator.Args().build()
        dehydrator = StandardDataclassDehydrator.Args().build()
        msg = hydrator(
            data={"from": "alice", "$ref": "#/defs/A", "body": "hi"},
            datacls=_AliasedPayload,
        )
        self.assertEqual(msg, _AliasedPayload(from_="alice", ref="#/defs/A", body="hi"))
        self.assertEqual(
            dehydrator(instance=msg),
            {"from": "alice", "$ref": "#/defs/A", "body": "hi"},
        )

        alias_schema = js(dtype=_AliasedPayload)
        self.assertIn("from", alias_schema["properties"])
        self.assertIn("$ref", alias_schema["properties"])
        self.assertEqual(alias_schema["required"], ["from", "$ref"])

        collect_hydrator = StandardDataclassHydrator.Args(collect_errors=True).build()
        with self.assertRaises(ExceptionGroup) as actx:
            collect_hydrator(data={"from": ""}, datacls=_AliasedPayload)
        payloads = [e.args[0] for e in actx.exception.exceptions]
        self.assertTrue(any(p.get("path") == ("from_",) for p in payloads))
        self.assertTrue(any(p.get("missing") == ["ref"] for p in payloads))


if __name__ == "__main__":
    unittest.main()
