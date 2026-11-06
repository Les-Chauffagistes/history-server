from src.utils.formatter import format_rows
from src.handlers.v1.utils.parsers import PoolDistributionParamsV1, PoolLastNParamsV1, PoolStatsParamsV1, WorkerLastNParamsV1, WorkerStatsParamsV1
from src.database.postgre import POOL
from datetime import datetime, timedelta

VALID_TABLES = {"forever": "worker_stats_raw", "daily": "worker_stats_1d"}
VALID_COLUMNS_NAMES = {"forever": "timestamp", "daily": "day"}


async def get_worker_stats(payload: WorkerStatsParamsV1):
    address = payload.address
    workername = payload.workername
    period = payload.period

    if any([address is None, workername is None, period is None]):
        raise ValueError("Missing parameters")

    table = VALID_TABLES.get(period)  # type: ignore stupid
    if table is None:
        raise ValueError("Bad period")

    column = VALID_COLUMNS_NAMES.get(period)  # type: ignore stupid
    if column is None:
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

async def get_total_pool_stats():
    stats = await POOL.get().fetch(
        """
            SELECT SUM(avg_hashrate1h) "avg_hashrate1h", SUM(avg_hashrate1d) "avg_hashrate1d", day
            FROM public.worker_stats_1d
            GROUP BY day
            ORDER BY day ASC;
        """.strip(),
    )

    return format_rows(stats)

async def get_pool_stats(payload: PoolStatsParamsV1):
    address = payload.address

    if address is None:
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

# Les workers d'un même passage du crawler (archive_stats) sont écrits dans une seule transaction :
# leurs timestamps sont identiques (ou séparés de quelques secondes). Un "échantillon" = toutes les lignes
# d'une adresse dans cette fenêtre, en amont du dernier timestamp <= at.
DISTRIBUTION_BATCH_WINDOW = timedelta(seconds=60)
# Le crawler échantillonne toutes les 30 min (DELAY_BETWEEN_REQUESTS). Au-delà de 4 échantillons manqués
# on refuse de répondre plutôt que de servir une répartition obsolète.
DISTRIBUTION_MAX_SAMPLE_AGE = timedelta(hours=2)


class DistributionNotFound(Exception):
    """Aucun échantillon exploitable à la date demandée (données purgées, trou de collecte, adresse inconnue)."""


def build_distribution(rows: list, at: datetime) -> list[dict]:
    """Transforme l'échantillon de poids en parts (fractions 0-1, somme = 1).

    `avg_weight` est le pourcentage (par adresse, fenêtre glissante côté pool-api) stocké par le crawler.
    On renormalise par la somme de l'échantillon : le résultat ne dépend pas de l'échelle (0-1 ou 0-100)
    et la somme vaut 1 aux erreurs d'arrondi flottant près.
    """
    if not rows:
        raise DistributionNotFound("no data at or before the requested date")

    sampled_at = max(r["timestamp"] for r in rows)
    if at - sampled_at > DISTRIBUTION_MAX_SAMPLE_AGE:
        raise DistributionNotFound("no sample close enough to the requested date")

    weights = [(r["workername"], float(r["avg_weight"] or 0)) for r in rows]
    total = sum(w for _, w in weights)
    if total <= 0:
        raise DistributionNotFound("no positive weight in the sample")

    return sorted(
        ({"workername": name, "part": w / total, "sampled_at": sampled_at} for name, w in weights),
        key=lambda e: (-e["part"], e["workername"]),
    )


async def get_distribution_at(payload: PoolDistributionParamsV1) -> list[dict]:
    rows = await POOL.get().fetch(
        """
            WITH ref AS (
                SELECT max(timestamp) AS ts
                FROM public.worker_stats_raw
                WHERE "user" = $1 AND timestamp <= $2::timestamptz
            )
            SELECT DISTINCT ON (w.worker_id) w.worker_id AS workername, w.avg_weight, w.timestamp
            FROM public.worker_stats_raw w
            JOIN ref ON w.timestamp <= ref.ts AND w.timestamp > ref.ts - $3::interval
            WHERE w."user" = $1
            ORDER BY w.worker_id, w.timestamp DESC
        """.strip(),
        payload.address,
        payload.at,
        DISTRIBUTION_BATCH_WINDOW,
    )
    return build_distribution(rows, payload.at)
