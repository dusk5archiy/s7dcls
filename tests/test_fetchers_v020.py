from __future__ import annotations

import json
import os
import tempfile
import unittest
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Annotated, Any
from unittest.mock import patch

from s7dcls import (
    AggregateDataclassSource,
    AggregateDictFetcher,
    ChainDataclassFetcher,
    ChainDataclassHydrator,
    ChainDataclassSource,
    DecoratedDictFetcher,
    DictFetcherProtocol,
    Gt,
    JsonFileDictLoaderWorker,
    KeyGateDictTransform,
    KeyPathDictTransform,
    NoCasePrefixGate,
    PrefixGate,
    PrefixRemover,
    RawFileDictFetcher,
    RawJsonDictFetcher,
    RawTomlDictFetcher,
    ScaffoldDataclassDehydratorFactory,
    ScaffoldDataclassHydratorFactory,
    ScaffoldDataclassKwargsResolver,
    SequenceDictTransform,
    SequenceTransform,
    StandardDataclassDehydrator,
    StandardDataclassHydrator,
    StandardDataclassSource,
    StandardFileDictFetcher,
    StandardFileDictLoader,
    StandardJsonCoercer,
    StandardShellDictFetcher,
    StandardStringCoercer,
    StandardUncoercer,
    StandardValidator,
    TomlFileDictLoaderWorker,
    UpperTransform,
)


@dataclass(kw_only=True, frozen=True)
class _StubDictFetcher(DictFetcherProtocol):
    payload: Mapping[str, Any]

    def __call__(self) -> Mapping[str, Any]:
        return self.payload


@dataclass(kw_only=True, frozen=True)
class NestedChild:
    _internal_tag: str
    count: Annotated[int, Gt(limit=0)] = 1


@dataclass(kw_only=True, frozen=True)
class SampleSettings:
    _runtime_dir: Path = Path("/tmp/default")
    port: Annotated[int, Gt(limit=0)] = 8000
    enabled: bool = False
    tags: tuple[str, ...] = ()
    child: NestedChild = field(
        default_factory=lambda: NestedChild(_internal_tag="default", count=1)
    )


@dataclass(kw_only=True, frozen=True)
class RequiredSplitSettings:
    host: str
    port: int


ENV_CLASS_PROJ = SequenceTransform(
    transforms=(PrefixRemover(prefix="_"), UpperTransform())
)
ENV_DATA_PROJ = UpperTransform()
APP_GATE = NoCasePrefixGate(prefix="__APP__")

STRICT_JSON_KR = ScaffoldDataclassKwargsResolver(
    coercer=StandardJsonCoercer.Args().build(),
)
ENV_JSON_KR = ScaffoldDataclassKwargsResolver(
    coercer=StandardJsonCoercer.Args().build(),
    class_key_projection=ENV_CLASS_PROJ,
    data_key_projection=ENV_DATA_PROJ,
    extra_keys_allowed=True,
)
ENV_SHELL_KR = ScaffoldDataclassKwargsResolver(
    coercer=StandardStringCoercer.Args().build(),
    class_key_projection=ENV_CLASS_PROJ,
    data_key_projection=ENV_DATA_PROJ,
    extra_keys_allowed=True,
)


class TestFileDictLoadersAndFetchersV020(unittest.TestCase):
    def test_file_dict_loader_returns_none_for_unsupported_suffix(self) -> None:
        json_loader = JsonFileDictLoaderWorker()
        toml_loader = TomlFileDictLoaderWorker()

        self.assertIsNone(json_loader(Path("config.toml")))
        self.assertIsNone(toml_loader(Path("config.json")))
        self.assertEqual(json_loader(Path("/nonexistent/config.json")), {})
        self.assertEqual(toml_loader(Path("/nonexistent/config.toml")), {})

    def test_standard_file_dict_loader_raises_on_unsupported_suffix(self) -> None:
        loader = StandardFileDictLoader.Args().build()
        with self.assertRaises(ValueError):
            loader(Path("/nonexistent/config.jsno"))

    def test_custom_file_dict_loader_extends_raw_file_dict_fetcher(self) -> None:
        def kv_loader(file: Path) -> dict[str, Any] | None:
            if file.suffix.lower() != ".kv":
                return None
            if not file.is_file():
                return {}
            result: dict[str, Any] = {}
            for line in file.read_text(encoding="utf-8").splitlines():
                k, v = line.split("=", 1)
                result[k.strip()] = v.strip()
            return result

        custom_loader = StandardFileDictLoader.Args(
            loaders=(JsonFileDictLoaderWorker(), TomlFileDictLoaderWorker(), kv_loader)
        ).build()

        with tempfile.TemporaryDirectory() as tmp:
            fp = Path(tmp) / "app.kv"
            fp.write_text("port=5050\nenabled=true\n", encoding="utf-8")
            settings = ChainDataclassFetcher(
                source=StandardDataclassSource.Args(
                    dict_fetcher=RawFileDictFetcher(file=fp, loader=custom_loader),
                    coercer=StandardStringCoercer.Args().build(),
                ).build(),
                datacls=SampleSettings,
            )()
            self.assertEqual(settings.port, 5050)
            self.assertTrue(settings.enabled)

    def test_dict_transforms_compose_for_push_data(self) -> None:
        cleaner = SequenceDictTransform(
            transforms=(
                KeyPathDictTransform(key_path=("app", "svc")),
                KeyGateDictTransform(key_gate=PrefixGate(prefix="cfg_")),
            )
        )
        cleaned = cleaner(
            {
                "app": {
                    "svc": {
                        "cfg_host": "10.0.0.1",
                        "CFG_host": "ignored",
                        "other": 123,
                    }
                }
            }
        )
        self.assertEqual(cleaned, {"host": "10.0.0.1"})

    def test_raw_json_preserves_native_types(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fp = Path(tmp) / "cfg.json"
            payload = {
                "port": 8080,
                "enabled": True,
                "ratio": 1.5,
                "tags": ["a", "b"],
                "nested": {"k": None},
            }
            fp.write_text(json.dumps(payload), encoding="utf-8")
            result = RawJsonDictFetcher(file=fp)()
            self.assertEqual(result, payload)

    def test_raw_json_missing_file_returns_empty(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fp = Path(tmp) / "missing.json"
            self.assertEqual(RawJsonDictFetcher(file=fp)(), {})

    def test_raw_json_non_dict_raises(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fp = Path(tmp) / "bad.json"
            fp.write_text("[1, 2, 3]", encoding="utf-8")
            with self.assertRaises(ValueError):
                RawJsonDictFetcher(file=fp)()

    def test_decorated_dict_fetcher_key_path_and_standard_file_key_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fp = Path(tmp) / "cfg.json"
            fp.write_text(
                json.dumps({"app": {"fleet": {"port": 9000, "enabled": True}}}),
                encoding="utf-8",
            )
            self.assertEqual(
                StandardFileDictFetcher.Args(
                    file=fp, key_path=("app", "fleet")
                ).build()(),
                {"port": 9000, "enabled": True},
            )
            self.assertEqual(
                StandardFileDictFetcher.Args(
                    file=fp, key_path=("app", "missing")
                ).build()(),
                {},
            )

        bad_key_path = DecoratedDictFetcher(
            dict_fetcher=_StubDictFetcher(payload={"app": 123}),
            dict_transform=KeyPathDictTransform(key_path=("app", "fleet")),
        )
        with self.assertRaises(ValueError):
            bad_key_path()

    def test_aggregate_dict_fetcher_merges_in_order(self) -> None:
        agg = AggregateDictFetcher(
            dict_fetchers=(
                _StubDictFetcher(payload={"a": 1, "b": 2}),
                _StubDictFetcher(payload={"b": 20, "c": 30}),
            )
        )
        self.assertEqual(agg(), {"a": 1, "b": 20, "c": 30})

    def test_toml_fetcher_and_standard_file_source(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fp = Path(tmp) / "cfg.toml"
            fp.write_text(
                '[service]\n_runtime_dir = "/opt/run"\nport = 7777\nenabled = true\n'
                'tags = ["x", "y"]\n'
                '[service.child]\n_internal_tag = "toml"\ncount = 3\n',
                encoding="utf-8",
            )
            raw = RawTomlDictFetcher(file=fp)()
            self.assertEqual(raw["service"]["port"], 7777)

            settings = ChainDataclassFetcher(
                source=StandardDataclassSource.Args(
                    dict_fetcher=StandardFileDictFetcher.Args(
                        file=fp, key_path=("service",)
                    ).build()
                ).build(),
                datacls=SampleSettings,
            )()
            self.assertEqual(settings._runtime_dir, Path("/opt/run"))
            self.assertEqual(settings.port, 7777)
            self.assertTrue(settings.enabled)
            self.assertEqual(settings.tags, ("x", "y"))
            self.assertEqual(settings.child, NestedChild(_internal_tag="toml", count=3))

    def test_prefix_gate_vs_nocase_prefix_gate(self) -> None:
        data = _StubDictFetcher(payload={"APP_a": 1, "app_b": 2, "OTHER": 3})
        exact = DecoratedDictFetcher(
            dict_fetcher=data,
            dict_transform=KeyGateDictTransform(key_gate=PrefixGate(prefix="APP_")),
        )()
        nocase = DecoratedDictFetcher(
            dict_fetcher=data,
            dict_transform=KeyGateDictTransform(
                key_gate=NoCasePrefixGate(prefix="APP_")
            ),
        )()
        self.assertEqual(exact, {"a": 1})
        self.assertEqual(nocase, {"a": 1, "b": 2})


class TestDataclassKwargsResolversAndSourcesV020(unittest.TestCase):
    def test_standard_validator_supports_args_build_and_default_init(self) -> None:
        v1 = StandardValidator.Args().build()
        v2 = StandardValidator()
        v1(value=42, dtype=Annotated[int, Gt(limit=0)])
        v2(value=42, dtype=Annotated[int, Gt(limit=0)])
        with self.assertRaises(ValueError):
            v1(value=0, dtype=Annotated[int, Gt(limit=0)])

    def test_standard_dataclass_source_string_mode_for_shell_and_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fp = Path(tmp) / "env.json"
            fp.write_text(
                json.dumps({"port": "7070", "enabled": "true"}), encoding="utf-8"
            )
            from_json = ChainDataclassFetcher(
                source=StandardDataclassSource.Args(
                    dict_fetcher=StandardFileDictFetcher.Args(file=fp).build(),
                    coercer=StandardStringCoercer.Args().build(),
                ).build(),
                datacls=SampleSettings,
            )()
            self.assertEqual(from_json.port, 7070)
            self.assertTrue(from_json.enabled)

        with patch.dict(
            os.environ, {"__APP__port": "6060", "__APP__enabled": "true"}, clear=True
        ):
            from_shell = ChainDataclassFetcher(
                source=StandardDataclassSource.Args(
                    dict_fetcher=StandardShellDictFetcher.Args(
                        key_gate=APP_GATE
                    ).build(),
                    coercer=StandardStringCoercer.Args().build(),
                ).build(),
                datacls=SampleSettings,
            )()
            self.assertEqual(from_shell.port, 6060)
            self.assertTrue(from_shell.enabled)

    def test_reusable_push_with_dict_transform_and_kwargs_resolver(self) -> None:
        svc_cleaner = KeyGateDictTransform(key_gate=PrefixGate(prefix="svc."))
        app_cleaner = KeyGateDictTransform(key_gate=APP_GATE)

        partial_1 = STRICT_JSON_KR(
            data=svc_cleaner({"svc.host": "10.0.0.1", "SVC.host": "ignored", "x": 1}),
            datacls=RequiredSplitSettings,
        )
        partial_2 = ENV_SHELL_KR(
            data=app_cleaner({"__APP__PORT": "443", "__APP__EXTRA": "x"}),
            datacls=RequiredSplitSettings,
        )
        self.assertEqual(partial_1, {"host": "10.0.0.1"})
        self.assertEqual(partial_2, {"port": 443})
        self.assertEqual(
            RequiredSplitSettings(**{**partial_1, **partial_2}),
            RequiredSplitSettings(host="10.0.0.1", port=443),
        )

    def test_standard_hydrator_reusable_push_on_clean_dicts(self) -> None:
        cleaner = KeyGateDictTransform(key_gate=PrefixGate(prefix="svc."))
        hydrator = StandardDataclassHydrator.Args().build()

        s1 = hydrator(
            data=cleaner(
                {
                    "svc._runtime_dir": "/var/run",
                    "svc.port": 8123,
                    "svc.enabled": True,
                    "SVC.port": 9999,
                }
            ),
            datacls=SampleSettings,
        )
        s2 = hydrator(
            data=cleaner({"svc.port": 9123}),
            datacls=SampleSettings,
        )
        self.assertEqual(s1._runtime_dir, Path("/var/run"))
        self.assertEqual(s1.port, 8123)
        self.assertTrue(s1.enabled)
        self.assertEqual(s2.port, 9123)
        self.assertFalse(s2.enabled)

    def test_s7dcls_defaults_to_no_project_key_projection(self) -> None:
        hydrator = StandardDataclassHydrator.Args().build()
        settings = hydrator(
            data={"_runtime_dir": "/var/run", "port": 8123, "enabled": True},
            datacls=SampleSettings,
        )
        self.assertEqual(settings._runtime_dir, Path("/var/run"))
        self.assertEqual(settings.port, 8123)

        with self.assertRaises(ValueError):
            hydrator(data={"runtime_dir": "/var/run"}, datacls=SampleSettings)

    def test_layered_json_and_shell_strict_provenance(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fp = Path(tmp) / "ui.json"
            fp.write_text(
                json.dumps(
                    {
                        "__APP__RUNTIME_DIR": "/from/json",
                        "__APP__PORT": 8080,
                        "__APP__ENABLED": True,
                        "__APP__TAGS": ["j1", "j2"],
                        "__APP__CHILD": {"_internal_tag": "from_json", "count": 4},
                    }
                ),
                encoding="utf-8",
            )

            env = {
                "__APP__PORT": "9090",
                "__APP__UNRELATED_KEY": "ignored",
            }
            with patch.dict(os.environ, env, clear=True):
                settings = ChainDataclassFetcher(
                    source=AggregateDataclassSource(
                        sources=(
                            ChainDataclassSource(
                                dict_fetcher=StandardFileDictFetcher.Args(
                                    file=fp, key_gate=APP_GATE
                                ).build(),
                                kwargs_resolver=ENV_JSON_KR,
                            ),
                            ChainDataclassSource(
                                dict_fetcher=StandardShellDictFetcher.Args(
                                    key_gate=APP_GATE
                                ).build(),
                                kwargs_resolver=ENV_SHELL_KR,
                            ),
                        )
                    ),
                    datacls=SampleSettings,
                )()

            self.assertEqual(settings._runtime_dir, Path("/from/json"))
            self.assertEqual(settings.port, 9090)
            self.assertTrue(settings.enabled)
            self.assertEqual(settings.tags, ("j1", "j2"))
            self.assertEqual(
                settings.child, NestedChild(_internal_tag="from_json", count=4)
            )

    def test_partial_sources_can_split_required_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fp = Path(tmp) / "partial.json"
            fp.write_text(json.dumps({"host": "127.0.0.1"}), encoding="utf-8")

            with patch.dict(os.environ, {"__APP__PORT": "8088"}, clear=True):
                settings = ChainDataclassFetcher(
                    source=AggregateDataclassSource(
                        sources=(
                            StandardDataclassSource.Args(
                                dict_fetcher=StandardFileDictFetcher.Args(
                                    file=fp
                                ).build()
                            ).build(),
                            ChainDataclassSource(
                                dict_fetcher=StandardShellDictFetcher.Args(
                                    key_gate=APP_GATE
                                ).build(),
                                kwargs_resolver=ENV_SHELL_KR,
                            ),
                        )
                    ),
                    datacls=RequiredSplitSettings,
                )()
            self.assertEqual(
                settings, RequiredSplitSettings(host="127.0.0.1", port=8088)
            )

    def test_json_source_stays_strict_even_when_layered_with_shell(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fp = Path(tmp) / "bad_type.json"
            fp.write_text(json.dumps({"port": "8080"}), encoding="utf-8")

            with patch.dict(os.environ, {"__APP__ENABLED": "true"}, clear=True):
                fetcher = ChainDataclassFetcher(
                    source=AggregateDataclassSource(
                        sources=(
                            StandardDataclassSource.Args(
                                dict_fetcher=StandardFileDictFetcher.Args(
                                    file=fp
                                ).build()
                            ).build(),
                            ChainDataclassSource(
                                dict_fetcher=StandardShellDictFetcher.Args(
                                    key_gate=APP_GATE
                                ).build(),
                                kwargs_resolver=ENV_SHELL_KR,
                            ),
                        )
                    ),
                    datacls=SampleSettings,
                )
                with self.assertRaises(TypeError):
                    fetcher()

    def test_root_key_projection_does_not_leak_into_nested_dataclass(self) -> None:
        shell_source = ChainDataclassSource(
            dict_fetcher=StandardShellDictFetcher.Args(key_gate=APP_GATE).build(),
            kwargs_resolver=ENV_SHELL_KR,
        )

        with patch.dict(
            os.environ,
            {
                "__APP__RUNTIME_DIR": "/ok",
                "__APP__CHILD": json.dumps({"_internal_tag": "exact", "count": 2}),
            },
            clear=True,
        ):
            settings = ChainDataclassFetcher(
                source=shell_source,
                datacls=SampleSettings,
            )()
            self.assertEqual(settings._runtime_dir, Path("/ok"))
            self.assertEqual(
                settings.child, NestedChild(_internal_tag="exact", count=2)
            )

        with patch.dict(
            os.environ,
            {
                "__APP__CHILD": json.dumps({"INTERNAL_TAG": "leaked", "COUNT": 2}),
            },
            clear=True,
        ):
            fetcher = ChainDataclassFetcher(
                source=shell_source,
                datacls=SampleSettings,
            )
            with self.assertRaises(ValueError):
                fetcher()

        with patch.dict(
            os.environ,
            {
                "__APP__CHILD": json.dumps(
                    {"_internal_tag": "ok", "count": 2, "extra": 1}
                ),
            },
            clear=True,
        ):
            fetcher = ChainDataclassFetcher(
                source=shell_source,
                datacls=SampleSettings,
            )
            with self.assertRaises(ValueError):
                fetcher()

    def test_chain_dataclass_hydrator_decouples_root_and_nested(self) -> None:
        hydrator = ChainDataclassHydrator(kwargs_resolver=ENV_JSON_KR)

        result = hydrator(
            data={
                "RUNTIME_DIR": "/hydrated",
                "CHILD": {"_internal_tag": "nested", "count": 5},
                "IGNORED": 123,
            },
            datacls=SampleSettings,
        )
        self.assertEqual(result._runtime_dir, Path("/hydrated"))
        self.assertEqual(result.child, NestedChild(_internal_tag="nested", count=5))

        with self.assertRaises(ValueError):
            hydrator(
                data={"CHILD": {"INTERNAL_TAG": "should_fail", "count": 5}},
                datacls=SampleSettings,
            )

    def test_value_checkers_enforced_through_hydrator_and_kwargs_resolver(self) -> None:
        hydrator = StandardDataclassHydrator.Args().build()
        with self.assertRaises(ValueError):
            hydrator(data={"port": 0}, datacls=SampleSettings)

    def test_standard_json_coercer_rejects_string_int(self) -> None:
        coercer = StandardJsonCoercer.Args().build()
        self.assertEqual(coercer(value=42, dtype=int), 42)
        with self.assertRaises(TypeError):
            coercer(value="42", dtype=int)

    def test_eager_fail_fast_even_when_higher_layer_overrides(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fp = Path(tmp) / "broken_lower.json"
            fp.write_text(json.dumps({"port": "8080"}), encoding="utf-8")

            with patch.dict(os.environ, {"__APP__PORT": "9090"}, clear=True):
                fetcher = ChainDataclassFetcher(
                    source=AggregateDataclassSource(
                        sources=(
                            StandardDataclassSource.Args(
                                dict_fetcher=StandardFileDictFetcher.Args(
                                    file=fp
                                ).build()
                            ).build(),
                            ChainDataclassSource(
                                dict_fetcher=StandardShellDictFetcher.Args(
                                    key_gate=APP_GATE
                                ).build(),
                                kwargs_resolver=ENV_SHELL_KR,
                            ),
                        )
                    ),
                    datacls=SampleSettings,
                )
                with self.assertRaises(TypeError):
                    fetcher()

    def test_custom_callable_source_returns_python_objects_directly(self) -> None:
        def direct_source(*, datacls: type[Any]) -> Mapping[str, Any]:
            return {
                "_runtime_dir": Path("/direct"),
                "child": NestedChild(_internal_tag="direct", count=9),
            }

        with tempfile.TemporaryDirectory() as tmp:
            fp = Path(tmp) / "override.json"
            fp.write_text(json.dumps({"port": 5555}), encoding="utf-8")
            settings = ChainDataclassFetcher(
                source=AggregateDataclassSource(
                    sources=(
                        direct_source,
                        StandardDataclassSource.Args(
                            dict_fetcher=StandardFileDictFetcher.Args(file=fp).build()
                        ).build(),
                    )
                ),
                datacls=SampleSettings,
            )()
        self.assertEqual(settings._runtime_dir, Path("/direct"))
        self.assertEqual(settings.port, 5555)
        self.assertEqual(settings.child, NestedChild(_internal_tag="direct", count=9))

    def test_aggregate_dataclass_source_composes_reusable_source_stack(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fp = Path(tmp) / "base.json"
            fp.write_text(json.dumps({"host": "127.0.0.1"}), encoding="utf-8")

            combined = AggregateDataclassSource(
                sources=(
                    StandardDataclassSource.Args(
                        dict_fetcher=StandardFileDictFetcher.Args(file=fp).build()
                    ).build(),
                    ChainDataclassSource(
                        dict_fetcher=StandardShellDictFetcher.Args(
                            key_gate=APP_GATE
                        ).build(),
                        kwargs_resolver=ENV_SHELL_KR,
                    ),
                )
            )
            with patch.dict(os.environ, {"__APP__PORT": "9999"}, clear=True):
                self.assertEqual(
                    combined(datacls=RequiredSplitSettings),
                    {"host": "127.0.0.1", "port": 9999},
                )
                settings = ChainDataclassFetcher(
                    source=combined,
                    datacls=RequiredSplitSettings,
                )()
            self.assertEqual(
                settings, RequiredSplitSettings(host="127.0.0.1", port=9999)
            )

    def test_nested_dataclass_hydrator_factory_controls_extra_keys_policy(self) -> None:
        permissive_coercer = StandardJsonCoercer.Args(
            dataclass_hydrator_factory=ScaffoldDataclassHydratorFactory(
                extra_keys_allowed=True
            ),
        ).build()
        hydrator = ChainDataclassHydrator(
            kwargs_resolver=ScaffoldDataclassKwargsResolver(coercer=permissive_coercer),
        )

        result = hydrator(
            data={"child": {"_internal_tag": "ok", "count": 2, "extra": "ignored"}},
            datacls=SampleSettings,
        )
        self.assertEqual(result.child, NestedChild(_internal_tag="ok", count=2))

    def test_dehydrator_factory_and_standard_dehydrator_roundtrip(self) -> None:
        instance = SampleSettings(
            _runtime_dir=Path("/run/sim"),
            port=9090,
            enabled=True,
            tags=("a", "b"),
            child=NestedChild(_internal_tag="inner", count=3),
        )
        dehydrator = StandardDataclassDehydrator.Args().build()
        raw = dehydrator(instance=instance)
        self.assertEqual(
            raw,
            {
                "_runtime_dir": "/run/sim",
                "port": 9090,
                "enabled": True,
                "tags": ["a", "b"],
                "child": {"_internal_tag": "inner", "count": 3},
            },
        )

        uncoercer = StandardUncoercer.Args(
            dataclass_dehydrator_factory=ScaffoldDataclassDehydratorFactory(
                class_key_projection=PrefixRemover(prefix="_")
            )
        ).build()
        projected = uncoercer(value=instance)
        self.assertEqual(projected["runtime_dir"], "/run/sim")
        self.assertEqual(projected["child"], {"internal_tag": "inner", "count": 3})


if __name__ == "__main__":
    unittest.main()
