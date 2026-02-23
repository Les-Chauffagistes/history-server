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