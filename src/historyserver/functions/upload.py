from .database.postgre import Postgre
from ..models.User import User
from ..functions.converter import from_string_to_number
from historyserver.init import log

async def archive_stats(user_id: str, user: User):
    connection = await Postgre.get_connection("chauffagistes")
    log.debug(user)
    records = [
        (
            record["workername"],
            from_string_to_number(record["hashrate1m"]),
            from_string_to_number(record["hashrate5m"]),
            from_string_to_number(record["hashrate1hr"]),
            from_string_to_number(record["hashrate1d"]),
            from_string_to_number(record["hashrate7d"]),
            0,
            user_id,
        )
        for record in user["worker"]
    ]

    async with connection.transaction():
        await connection.copy_records_to_table(
            "worker_stats_raw",
            records=records,
            columns=[
                "worker_id",
                "avg_hashrate1m",
                "avg_hashrate5m",
                "avg_hashrate1h",
                "avg_hashrate1d",
                "avg_hashrate7d",
                "avg_weight",
                "user",
            ],
        )