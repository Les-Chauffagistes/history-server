import asyncio
from typing import NoReturn
from ..functions.upload import archive_stats
from ..init import log
from ..apis.chauffagistes_pool.routes import get_every_user_data
from asyncio import CancelledError

DELAY_BETWEEN_REQUESTS = 60 * 30
async def gather_stats() -> NoReturn:
    while True:
        try:
            payload = await get_every_user_data()
            for user_id, pool_data in payload["users"].items():
                try:
                    await archive_stats(user_id, pool_data, payload["repartition"])

                except Exception:
                    log.error("Error while archiving stats for user", user_id)
                    continue
        
        except CancelledError:
            raise

        except Exception:
            log.error()
        
        finally:
            await asyncio.sleep(DELAY_BETWEEN_REQUESTS)