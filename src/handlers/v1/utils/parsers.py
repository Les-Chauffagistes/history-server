from typing import Literal
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