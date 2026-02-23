from utils.formatter import format_rows
from handlers.v1.utils.parsers import PoolStatsParamsV1, WorkerStatsParamsV1
from database.postgre import POOL

VALID_TABLES = {"forever": "worker_stats_raw", "daily": "worker_stats_1d"}
VALID_COLUNMS_NAMES = {"forever": "timestamp", "daily": "day"}


async def get_worker_stats(payload: WorkerStatsParamsV1):
    address = payload.address
    workername = payload.workername
    period = payload.period

    if any([address == None, workername == None, period == None]):
        raise ValueError("Missing parameters")

    table = VALID_TABLES.get(period)  # type: ignore stupid
    if table == None:
        raise ValueError("Bad period")

    column = VALID_COLUNMS_NAMES.get(period)  # type: ignore stupid
    if column == None:
        raise ValueError("Bad period")

    ## NOTICE
    # SELECT {column} et ORDER BY {column} ne peuvent être remplacés par $3 et seraient ignorés
    stats = await POOL.get().fetch(
        f"""   
            SELECT {column}, avg_hashrate1m, avg_hashrate5m, avg_hashrate1h, avg_hashrate1d, avg_hashrate7d, avg_weight
            FROM {table}
            WHERE (
                worker_id = $1
            AND
                "user" = $2
            )
            ORDER BY {column} ASC
        """.strip(),
        workername,
        address,
    )

    return format_rows(stats)

async def get_pool_stats(payload: PoolStatsParamsV1):
    address = payload.address

    if address == None:
        raise ValueError("Missing parameters")

    stats = await POOL.get().fetch(
        """
            SELECT SUM(avg_hashrate1h) "avg_hashrate1h", SUM(avg_hashrate1d) "avg_hashrate1d", date_trunc('minute', timestamp) "timestamp"
            FROM public.worker_stats_raw 
            WHERE "user" = $1
            GROUP BY date_trunc('minute', timestamp)
            ORDER BY date_trunc('minute', timestamp) DESC;
        """.strip(),
        address,
    )

    return format_rows(stats)