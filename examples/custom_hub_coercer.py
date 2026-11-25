from __future__ import annotations

from dataclasses import dataclass
from ipaddress import IPv4Address
from typing import Any

from s7dcls import CoerceResult, FirstMatchCoercerWorker, HubCoercer
from s7dcls.coercers.mechanism import ListCoercerWorker


@dataclass(kw_only=True, frozen=True)
class Ipv4CoercerWorker:
    def __call__(self, *, value: Any, dtype: Any) -> CoerceResult[IPv4Address] | None:
        if dtype is not IPv4Address:
            return None
        if isinstance(value, IPv4Address):
            return CoerceResult(value=value)
        if isinstance(value, str):
            return CoerceResult(value=IPv4Address(value))
        raise TypeError(
            {
                "value": value,
                "expected_type": str(IPv4Address),
                "got_type": str(type(value)),
            }
        )


def main() -> None:
    coercer = HubCoercer(
        spawner=lambda hub: FirstMatchCoercerWorker(
            workers=(ListCoercerWorker(hub=hub), Ipv4CoercerWorker())
        )
    )
    ips = coercer(value=["127.0.0.1", "10.0.0.1"], dtype=list[IPv4Address])
    assert ips == [IPv4Address("127.0.0.1"), IPv4Address("10.0.0.1")]
    print(ips)


if __name__ == "__main__":
    main()
