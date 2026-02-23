from utils.formatter import format_rows
from handlers.v1.utils.parsers import PoolLastNParamsV1, PoolStatsParamsV1, WorkerLastNParamsV1, WorkerStatsParamsV1
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

async def get_worker_stats_last_n(payload: WorkerLastNParamsV1):
    table = "worker_stats_raw" if payload.source == "forever" else "worker_stats_1d"
    col = "timestamp" if payload.source == "forever" else "day"
    # Pour daily, CURRENT_DATE évite le décalage horaire de NOW() :
    # les buckets commencent à 00:00:00, comparer avec NOW() (ex. 15:00) exclurait
    # le bucket du jour précédent alors qu'il devrait être inclus.
    origin = "NOW()" if payload.source == "forever" else "CURRENT_DATE"
    rows = await POOL.get().fetch(
        f"""
            SELECT {col}, avg_hashrate1m, avg_hashrate5m, avg_hashrate1h,
                   avg_hashrate1d, avg_hashrate7d, avg_weight
            FROM {table}
            WHERE worker_id = $1 AND "user" = $2
              AND {col} >= {origin} - $3 * INTERVAL '1 day'
            ORDER BY {col} ASC
        """.strip(),
        payload.workername,
        payload.address,
        payload.n,
    )
    return format_rows(rows)

async def get_pool_stats_last_n(payload: PoolLastNParamsV1):
    if payload.source == "forever":
        col, table = "timestamp", "worker_stats_raw"
        group = "date_trunc('minute', timestamp)"
        select_col = f"{group} \"{col}\""
        origin = "NOW()"
    else:
        col, table = "day", "worker_stats_1d"
        group = "day"
        select_col = "day"
        origin = "CURRENT_DATE"
    rows = await POOL.get().fetch(
        f"""
            SELECT SUM(avg_hashrate1h) "avg_hashrate1h",
                   SUM(avg_hashrate1d) "avg_hashrate1d",
                   {select_col}
            FROM {table}
            WHERE "user" = $1
              AND {col} >= {origin} - $2 * INTERVAL '1 day'
            GROUP BY {group}
            ORDER BY {group} ASC
        """.strip(),
        payload.address,
        payload.n,
    )
    return format_rows(rows)

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