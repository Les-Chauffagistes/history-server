from typing import Generator
from core.models import PoolHistory, WorkerHistory, WorkersWeight


def serialize_worker_stats(data: Generator[dict]) -> Generator[WorkerHistory]:
    for row in data:
        yield {
            "timestamp": row["timestamp"] if "timestamp" in row else row["day"],
            "avg_hashrate1m": row["avg_hashrate1m"],
            "avg_hashrate5m": row["avg_hashrate5m"],
            "avg_hashrate1h": row["avg_hashrate1h"],
            "avg_hashrate1d": row["avg_hashrate1d"],
            "avg_hashrate7d": row["avg_hashrate7d"],
            "avg_weight": row["avg_weight"],
        }

def serialze_pool_stats(data: Generator[dict]) -> Generator[PoolHistory]:
    for row in data:
        yield {
            "timestamp": row["timestamp"],
            "avg_hashrate1h": row["avg_hashrate1h"],
            "avg_hashrate1d": row["avg_hashrate1d"],
        }

def serialze_pool_stats_last_n(data: Generator[dict]) -> Generator[PoolHistory]:
    for row in data:
        yield {
            "timestamp": row["timestamp"] if "timestamp" in row else row["day"],
            "avg_hashrate1h": row["avg_hashrate1h"],
            "avg_hashrate1d": row["avg_hashrate1d"],
        }

def serialyze_worker_weights(data: Generator[dict]) -> Generator[WorkersWeight]:
    for row in data:
        yield {
            "timestamp": row["timestamp"],
            "worker_id": row["worker_id"],
            "avg_weight": row["avg_weight"],
        }