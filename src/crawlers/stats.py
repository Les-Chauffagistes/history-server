import asyncio
from typing import NoReturn
from ..apis.chauffagistes_pool.utils.upload import archive_stats
from ..apis.chauffagistes_pool.routes import get_every_user_data
from chauff_cmn.callers.pools import PoolAPIClient
from asyncio import CancelledError


DELAY_BETWEEN_REQUESTS = 60 * 30
async def gather_stats(client: PoolAPIClient) -> NoReturn:
    # importer paresseusement le logger central pour éviter les importations circulaires
    import init as hs_init
    log = hs_init.log
    while True:
        try:
            payload = await client.get_cluster()
            for user_id, pool_data in payload.users.items():
                try:
                    await archive_stats(user_id, pool_data, payload.repartition)

                except Exception:
                    log.exception(f"Error while archiving stats for user {user_id}")

                    continue

        except CancelledError:
            raise

        except Exception:
            log.exception("Error in gather_stats loop")

        # hors du try/finally : une annulation (SIGTERM) doit interrompre le sleep immédiatement
        await asyncio.sleep(DELAY_BETWEEN_REQUESTS)