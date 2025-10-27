from historyserver.models.Repartition import Repartition
from .database.postgre import Postgre
from ..models.User import User
from ..functions.converter import from_string_to_number
from historyserver.init import log

async def archive_stats(user_id: str, user: User, repartition: dict[str, Repartition]):
    connection = await Postgre.get_connection("chauffagistes")
    records = []
    for worker in user["worker"]:
        worker_name = worker["workername"].split(".")
        if len(worker_name) > 1:
            worker_name = worker_name[1]

        else:
            worker_name = "worker sans nom"

        records.append(
            (
                worker_name,
                from_string_to_number(worker["hashrate1m"]),
                from_string_to_number(worker["hashrate5m"]),
                from_string_to_number(worker["hashrate1hr"]),
                from_string_to_number(worker["hashrate1d"]),
                from_string_to_number(worker["hashrate7d"]),
                repartition.get(worker["workername"], {}).get("percentage", 0.0),
                user_id,
            )
        )

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