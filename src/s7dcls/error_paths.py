from __future__ import annotations

from dataclasses import dataclass, field
from types import TracebackType
from typing import Any

type PathSegment = str | int


def _to_path_segment(segment: Any) -> PathSegment:
    if isinstance(segment, str):
        return segment
    if isinstance(segment, int) and not isinstance(segment, bool):
        return segment
    return str(segment)


def _prepend_recursive(exc: BaseException, segment: PathSegment) -> None:
    if isinstance(exc, ExceptionGroup):
        for sub in exc.exceptions:
            _prepend_recursive(sub, segment)
        return
    if exc.args and isinstance(exc.args[0], dict):
        payload: dict[str, Any] = dict(exc.args[0])
        existing = payload.get("path", ())
        if isinstance(existing, tuple):
            payload["path"] = (segment, *existing)
        else:
            payload["path"] = (segment,)
        exc.args = (payload, *exc.args[1:])


@dataclass(kw_only=True, frozen=True, slots=True)
class ErrorPath:
    segment: Any
    batch: ErrorBatch | None = None

    @staticmethod
    def prepend(*, exc: BaseException, segment: Any) -> None:
        _prepend_recursive(exc, _to_path_segment(segment))

    def __enter__(self) -> None:
        return None

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> bool:
        if isinstance(exc, (TypeError, ValueError, ExceptionGroup)):
            self.prepend(exc=exc, segment=self.segment)
            if self.batch is not None and self.batch.collect:
                self.batch.extend(exc=exc)
                return True
        return False


@dataclass(kw_only=True, slots=True)
class ErrorBatch:
    collect: bool = True
    errors: list[Exception] = field(default_factory=list)

    def capture(self, *, segment: Any) -> ErrorPath:
        return ErrorPath(segment=segment, batch=self)

    def add(self, *, exc: Exception) -> None:
        if self.collect:
            self.errors.append(exc)
        else:
            raise exc

    def extend(self, *, exc: Exception | ExceptionGroup[Exception]) -> None:
        if isinstance(exc, ExceptionGroup):
            if self.collect:
                self.errors.extend(exc.exceptions)
            else:
                raise exc
        else:
            self.add(exc=exc)

    def raise_if_any(self) -> None:
        if not self.errors:
            return
        if len(self.errors) == 1:
            raise self.errors[0]
        raise ExceptionGroup("s7dcls", self.errors)


__all__ = ["ErrorBatch", "ErrorPath", "PathSegment"]
