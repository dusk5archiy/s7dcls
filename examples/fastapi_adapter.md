# FastAPI Adapter

```python
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from typing import Annotated, Any
from uuid import UUID, uuid4

from fastapi import Depends, FastAPI, HTTPException, Request

from s7dcls import (
    NonEmptyStr,
    StandardDataclassDehydrator,
    StandardDataclassHydrator,
    StandardJsonSchemaDescriber,
)

app = FastAPI()
hydrator = StandardDataclassHydrator.Args(collect_errors=True).build()
dehydrator = StandardDataclassDehydrator.Args().build()
json_schema = StandardJsonSchemaDescriber.Args(include_docstrings=True).build()


def s7_body[T](datacls: type[T]) -> Callable[..., Any]:
    async def dependency(request: Request) -> T:
        raw = await request.json()
        try:
            return hydrator(data=raw, datacls=datacls)  # type: ignore[arg-type]
        except ExceptionGroup as eg:
            raise HTTPException(
                status_code=422,
                detail=[exc.args[0] for exc in eg.exceptions],
            ) from None
        except (TypeError, ValueError) as exc:
            raise HTTPException(status_code=422, detail=[exc.args[0]]) from None

    return dependency


@dataclass(kw_only=True, frozen=True)
class CreateMessageReq:
    from_: Annotated[str, NonEmptyStr()] = field(metadata={"alias": "from"})
    text: Annotated[str, NonEmptyStr()]


@dataclass(kw_only=True, frozen=True)
class MessageResp:
    id: UUID
    from_: str = field(metadata={"alias": "from"})
    text: str
    created_at: datetime


@app.post(
    "/messages",
    openapi_extra={
        "requestBody": {
            "required": True,
            "content": {
                "application/json": {
                    "schema": json_schema(dtype=CreateMessageReq),
                }
            },
        }
    },
)
def create_message(
    body: CreateMessageReq = Depends(s7_body(CreateMessageReq)),
) -> dict[str, Any]:
    resp = MessageResp(
        id=uuid4(),
        from_=body.from_,
        text=body.text,
        created_at=datetime.now(),
    )
    return dehydrator(instance=resp)
```
