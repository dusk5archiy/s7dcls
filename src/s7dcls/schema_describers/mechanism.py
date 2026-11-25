from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from s7dcls.dict_transforms.protocol import DictTransformProtocol

JSON_SCHEMA_DRAFT_2020_12 = "https://json-schema.org/draft/2020-12/schema"

_PRIMITIVE_MAP: dict[str, dict[str, Any]] = {
    "bool": {"type": "boolean"},
    "int": {"type": "integer"},
    "float": {"type": "number"},
    "str": {"type": "string"},
    "none": {"type": "null"},
    "any": {},
    "path": {"type": "string", "format": "path"},
    "uuid": {"type": "string", "format": "uuid"},
    "datetime": {"type": "string", "format": "date-time"},
    "date": {"type": "string", "format": "date"},
    "timedelta": {"type": "number", "format": "duration-seconds"},
    "decimal": {"type": "string", "format": "decimal"},
}


def _apply_constraints(node: Mapping[str, Any], out: dict[str, Any]) -> dict[str, Any]:
    out_type = out.get("type")
    if "min" in node:
        out["minimum"] = node["min"]
    if "gt" in node:
        out["exclusiveMinimum"] = node["gt"]
    if "max" in node:
        out["maximum"] = node["max"]
    if "lt" in node:
        out["exclusiveMaximum"] = node["lt"]
    if "multiple_of" in node:
        out["multipleOf"] = node["multiple_of"]
    if node.get("non_empty"):
        out["minLength"] = max(1, int(out.get("minLength", 1)))
    if "pattern" in node:
        out["pattern"] = node["pattern"]
    if node.get("unique_items"):
        out["uniqueItems"] = True
    if "min_length" in node:
        limit = node["min_length"]
        if out_type == "array":
            out["minItems"] = limit
        elif out_type == "object":
            out["minProperties"] = limit
        else:
            out["minLength"] = limit
    if "max_length" in node:
        limit = node["max_length"]
        if out_type == "array":
            out["maxItems"] = limit
        elif out_type == "object":
            out["maxProperties"] = limit
        else:
            out["maxLength"] = limit
    if "description" in node:
        out["description"] = node["description"]
    return out


def _convert_node(
    node: Mapping[str, Any],
    *,
    defs: dict[str, dict[str, Any]],
    root_name: str | None,
    is_root: bool,
) -> dict[str, Any]:
    kind = node.get("type")
    if not isinstance(kind, str):
        raise TypeError(
            {
                "schema": dict(node),
                "expected_type": str(str),
                "got_type": str(type(kind)),
            }
        )

    out: dict[str, Any]
    if kind in _PRIMITIVE_MAP:
        out = dict(_PRIMITIVE_MAP[kind])
    elif kind == "literal":
        choices = list(node.get("choices", []))
        out = {"const": choices[0]} if len(choices) == 1 else {"enum": choices}
    elif kind == "enum":
        out = {"enum": list(node.get("choices", []))}
        if "name" in node:
            out["title"] = node["name"]
    elif kind == "array":
        items = node.get("items")
        out = {
            "type": "array",
            "items": _convert_node(items, defs=defs, root_name=root_name, is_root=False)
            if isinstance(items, Mapping)
            else {},
        }
        if node.get("unique"):
            out["uniqueItems"] = True
    elif kind == "tuple":
        items = list(node.get("items", []))
        out = {
            "type": "array",
            "prefixItems": [
                _convert_node(item, defs=defs, root_name=root_name, is_root=False)
                for item in items
            ],
            "minItems": len(items),
            "maxItems": len(items),
        }
    elif kind == "dict":
        val = node.get("value")
        out = {
            "type": "object",
            "additionalProperties": _convert_node(
                val, defs=defs, root_name=root_name, is_root=False
            )
            if isinstance(val, Mapping)
            else {},
        }
    elif kind == "union":
        variants = list(node.get("variants", []))
        out = {
            "anyOf": [
                _convert_node(v, defs=defs, root_name=root_name, is_root=False)
                for v in variants
            ]
        }
    elif kind in ("dataclass_ref", "alias_ref"):
        ref_name = str(node["name"])
        out = (
            {"$ref": "#"} if ref_name == root_name else {"$ref": f"#/$defs/{ref_name}"}
        )
    elif kind == "dataclass":
        name = str(node["name"])
        properties: dict[str, dict[str, Any]] = {}
        required: list[str] = []
        for field_entry in node.get("fields", []):
            field_name = str(field_entry["name"])
            field_schema = _convert_node(
                field_entry["schema"],
                defs=defs,
                root_name=root_name,
                is_root=False,
            )
            if "description" in field_entry:
                field_schema = {
                    **field_schema,
                    "description": field_entry["description"],
                }
            properties[field_name] = field_schema
            if field_entry.get("required", True):
                required.append(field_name)

        obj: dict[str, Any] = {
            "type": "object",
            "title": name,
            "properties": properties,
            "additionalProperties": False,
        }
        if required:
            obj["required"] = required
        if "description" in node:
            obj["description"] = node["description"]

        if not is_root:
            defs[name] = obj
            out = {"$ref": f"#/$defs/{name}"}
        else:
            out = obj
    else:
        raise ValueError({"schema": dict(node), "unknown_type": kind})

    _apply_constraints(node, out)

    if node.get("nullable"):
        if "anyOf" in out and isinstance(out["anyOf"], list):
            out["anyOf"] = [*out["anyOf"], {"type": "null"}]
        else:
            out = {"anyOf": [out, {"type": "null"}]}

    return out


@dataclass(kw_only=True, frozen=True)
class JsonSchemaDictTransform(DictTransformProtocol):
    def __call__(self, x: Mapping[str, Any]) -> dict[str, Any]:
        defs: dict[str, dict[str, Any]] = {}
        root_name = (
            str(x["name"]) if x.get("type") == "dataclass" and "name" in x else None
        )
        converted = _convert_node(x, defs=defs, root_name=root_name, is_root=True)
        out: dict[str, Any] = {"$schema": JSON_SCHEMA_DRAFT_2020_12, **converted}
        if defs:
            out["$defs"] = defs
        return out


__all__ = ["JSON_SCHEMA_DRAFT_2020_12", "JsonSchemaDictTransform"]
