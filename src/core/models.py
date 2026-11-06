from datetime import datetime
from typing import TypedDict


class WorkerHistory(TypedDict):
    timestamp: datetime
    avg_hashrate1m: int
    avg_hashrate5m: int
    avg_hashrate1h: int
    avg_hashrate1d: int
    avg_hashrate7d: int
    avg_weight: float

class PoolHistory(TypedDict):
    timestamp: datetime
    avg_hashrate1h: int
    avg_hashrate1d: int

class WorkersWeight(TypedDict):
    timestamp: datetime
    worker_id: str
    avg_weight: float


class PoolDistributionAt(TypedDict):
    workername: str
    part: float  # fraction 0-1
    sampled_at: str  # ISO 8601
