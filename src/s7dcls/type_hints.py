from __future__ import annotations

import operator
from collections.abc import Mapping
from dataclasses import dataclass, is_dataclass
from functools import lru_cache, reduce
from types import MappingProxyType, NoneType, UnionType
from typing import (
    Annotated,
    Any,
    Literal,
    TypeAliasType,
    Union,
    get_args,
    get_origin,
    get_type_hints,
)


@dataclass(kw_only=True, frozen=True)
class TaggedUnionSpec:
    field: str
    branches: Mapping[tuple[type[Any], Any], Any]
    allowed: tuple[Any, ...]
    allow_none: bool = False


@lru_cache(maxsize=512)
def get_cached_type_hints(cls: type[Any]) -> Mapping[str, Any]:
    return MappingProxyType(get_type_hints(cls, include_extras=True))


def _unwrap_alias_and_annotated(tp: Any) -> Any:
    while True:
        if isinstance(tp, TypeAliasType):
            tp = tp.__value__
        elif get_origin(tp) is Annotated:
            tp = get_args(tp)[0]
        else:
            return tp


def _substitute_type_vars(tp: Any, subst: Mapping[Any, Any]) -> Any:
    if tp in subst:
        return subst[tp]

    origin = get_origin(tp)
    if origin is None:
        return tp

    args = get_args(tp)
    if not args:
        return tp

    if origin is Annotated:
        base, *extras = args
        new_base = _substitute_type_vars(base, subst)
        if new_base is base:
            return tp
        return Annotated[(new_base, *extras)]

    if origin in (UnionType, Union):
        new_union_args = tuple(_substitute_type_vars(arg, subst) for arg in args)
        if new_union_args == args:
            return tp
        return reduce(operator.or_, new_union_args)

    new_args: list[Any] = []
    changed = False
    for arg in args:
        if arg is Ellipsis or arg == ():
            new_args.append(arg)
        elif isinstance(arg, list):
            sub_list = [_substitute_type_vars(item, subst) for item in arg]
            if sub_list != arg:
                changed = True
            new_args.append(sub_list)
        else:
            sub = _substitute_type_vars(arg, subst)
            if sub is not arg:
                changed = True
            new_args.append(sub)

    if not changed:
        return tp

    if len(new_args) == 1:
        return origin[new_args[0]]
    return origin[tuple(new_args)]


def _compute_dataclass_type(
    dtype: Any,
) -> tuple[type[Any], Mapping[str, Any]] | None:
    if isinstance(dtype, type) and is_dataclass(dtype):
        return dtype, get_cached_type_hints(dtype)

    origin = get_origin(dtype)
    if isinstance(origin, type) and is_dataclass(origin):
        params: tuple[Any, ...] = getattr(origin, "__parameters__", ())
        args = get_args(dtype)
        base_hints = get_cached_type_hints(origin)
        if not params or len(params) != len(args):
            return origin, base_hints
        subst = dict(zip(params, args, strict=True))
        resolved = {
            name: _substitute_type_vars(hint, subst)
            for name, hint in base_hints.items()
        }
        return origin, MappingProxyType(resolved)

    return None


@lru_cache(maxsize=512)
def _cached_resolve_dataclass_type(
    dtype: Any,
) -> tuple[type[Any], Mapping[str, Any]] | None:
    return _compute_dataclass_type(dtype)


def resolve_dataclass_type(
    dtype: Any,
) -> tuple[type[Any], Mapping[str, Any]] | None:
    try:
        return _cached_resolve_dataclass_type(dtype)
    except TypeError:
        return _compute_dataclass_type(dtype)


def _compute_tagged_union(dtype: Any) -> TaggedUnionSpec | None:
    if get_origin(dtype) not in (UnionType, Union):
        return None

    dataclass_branches: list[tuple[Any, Mapping[str, Any]]] = []
    allow_none = False
    for branch in get_args(dtype):
        raw_branch = _unwrap_alias_and_annotated(branch)
        if raw_branch is None or raw_branch is NoneType:
            allow_none = True
            continue
        resolved = resolve_dataclass_type(raw_branch)
        if resolved is None:
            return None
        dataclass_branches.append((branch, resolved[1]))

    if len(dataclass_branches) < 2:
        return None

    first_hints = dataclass_branches[0][1]
    common_fields = [
        name
        for name in first_hints
        if all(name in hints for _, hints in dataclass_branches[1:])
    ]

    candidates: list[TaggedUnionSpec] = []
    for field_name in common_fields:
        branch_map: dict[tuple[type[Any], Any], Any] = {}
        allowed: list[Any] = []
        valid = True

        for branch, hints in dataclass_branches:
            field_type = _unwrap_alias_and_annotated(hints[field_name])
            if get_origin(field_type) is not Literal:
                valid = False
                break
            tags = get_args(field_type)
            if not tags:
                valid = False
                break
            for tag in tags:
                key = (type(tag), tag)
                if key in branch_map:
                    valid = False
                    break
                branch_map[key] = branch
                allowed.append(tag)
            if not valid:
                break

        if valid and branch_map:
            candidates.append(
                TaggedUnionSpec(
                    field=field_name,
                    branches=MappingProxyType(branch_map),
                    allowed=tuple(allowed),
                    allow_none=allow_none,
                )
            )
            if len(candidates) > 1:
                return None

    return candidates[0] if len(candidates) == 1 else None


@lru_cache(maxsize=512)
def _cached_resolve_tagged_union(dtype: Any) -> TaggedUnionSpec | None:
    return _compute_tagged_union(dtype)


def resolve_tagged_union(dtype: Any) -> TaggedUnionSpec | None:
    try:
        return _cached_resolve_tagged_union(dtype)
    except TypeError:
        return _compute_tagged_union(dtype)


__all__ = [
    "TaggedUnionSpec",
    "get_cached_type_hints",
    "resolve_dataclass_type",
    "resolve_tagged_union",
]
