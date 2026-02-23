from database.postgre import POOL
from handlers.v1.utils.parsers import WorkersWeightParamsV1
from utils.formatter import format_rows



async def get_workers_weight(payload: WorkersWeightParamsV1):
    address = payload.address

    if address == None:
        raise ValueError("Missing parameters")

    stats = await POOL.get().fetch(
        """
            SELECT * FROM (
                    SELECT DISTINCT ON (worker_id) 
                        worker_id, 
                        avg_weight,
                        timestamp
                    FROM public.worker_stats_raw
                    WHERE "user" = $1
                    ORDER BY worker_id, timestamp DESC
                ) AS latest_records
                ORDER BY avg_weight DESC;
        """.strip(),
        address,
    )

    return format_rows(stats)