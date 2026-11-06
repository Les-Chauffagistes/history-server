import re
from datetime import datetime, timezone
from typing import Literal
from aiohttp import web
from aiohttp.web_request import Request
from dataclasses import dataclass

@dataclass(frozen=True)
class WorkerStatsParamsV1:
    address: str
    workername: str
    period: Literal["forever", "daily"]

def parse_worker_stats(request: Request):
    return WorkerStatsParamsV1(
        address = request.match_info["address"],
        workername = request.match_info["workername"],
        period = request.match_info["period"],
    )

@dataclass(frozen=True)
class PoolStatsParamsV1:
    address: str

def parse_pool_stats(request: Request):
    return PoolStatsParamsV1(
        address = request.match_info["address"],
    )

@dataclass(frozen=True)
class WorkersWeightParamsV1:
    address: str

def parse_workers_weight(request: Request):
    return WorkersWeightParamsV1(
        address = request.match_info["address"],
    )

@dataclass(frozen=True)
class WorkerLastNParamsV1:
    address: str
    workername: str
    source: Literal["forever", "daily"]
    n: int

def parse_worker_last_n(request: Request) -> WorkerLastNParamsV1:
    source = request.match_info["source"]
    if source not in ("forever", "daily"):
        raise web.HTTPBadRequest(reason="source must be 'forever' or 'daily'")
    try:
        n = int(request.match_info["n"])
        if n <= 0:
            raise ValueError
    except ValueError:
        raise web.HTTPBadRequest(reason="n must be a positive integer")
    if source == "forever" and n > 90:
        raise web.HTTPBadRequest(reason="raw data is only retained for 90 days")
    return WorkerLastNParamsV1(
        address=request.match_info["address"],
        workername=request.match_info["workername"],
        source=source,
        n=n,
    )

@dataclass(frozen=True)
class PoolLastNParamsV1:
    address: str
    source: Literal["forever", "daily"]
    n: int

def parse_pool_last_n(request: Request) -> PoolLastNParamsV1:
    source = request.match_info["source"]
    if source not in ("forever", "daily"):
        raise web.HTTPBadRequest(reason="source must be 'forever' or 'daily'")
    try:
        n = int(request.match_info["n"])
        if n <= 0:
            raise ValueError
    except ValueError:
        raise web.HTTPBadRequest(reason="n must be a positive integer")
    if source == "forever" and n > 90:
        raise web.HTTPBadRequest(reason="raw data is only retained for 90 days")
    return PoolLastNParamsV1(
        address=request.match_info["address"],
        source=source,
        n=n,
    )

@dataclass(frozen=True)
class PoolDistributionParamsV1:
    address: str
    at: datetime  # toujours timezone-aware, en UTC


def parse_iso_datetime(value: str | None) -> datetime:
    """Parse une date ISO 8601 avec fuseau obligatoire (ex. 2026-11-04T17:09:23Z ou ...+01:00)."""
    if not value:
        raise web.HTTPBadRequest(reason="at query param is required (ISO 8601 date)")
    # Un '+' non encodé dans une query string devient un espace : "…23+01:00" arrive en "…23 01:00".
    value = re.sub(r" (\d{2}:\d{2})$", r"+\1", value.strip())
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        raise web.HTTPBadRequest(reason="at must be a valid ISO 8601 date")
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise web.HTTPBadRequest(reason="at must include a timezone (e.g. 'Z' or '+00:00')")
    return parsed.astimezone(timezone.utc)


def parse_pool_distribution(request: Request) -> PoolDistributionParamsV1:
    at = parse_iso_datetime(request.query.get("at"))
    if at > datetime.now(timezone.utc):
        raise web.HTTPBadRequest(reason="at must not be in the future")
    return PoolDistributionParamsV1(address=request.match_info["address"], at=at)
