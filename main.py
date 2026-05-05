import asyncio

from src.utils.cors import cors
import init as hs_init
from init import GATHER_STATS, routes, PORT, app, log
from aiohttp import web
from src.crawlers.stats import gather_stats
import src.core


async def main():
    hs_init.log.info("Démarrage du serveur...")
    runner = web.AppRunner(app)
    await runner.setup()
    if PORT:
        site = web.TCPSite(runner, '0.0.0.0', PORT)
        await site.start()
    hs_init.log.info(f'Serveur interne en ligne sur localhost:{PORT}')
    if GATHER_STATS:
        await gather_stats()
    while True:
        await asyncio.Future()

if __name__ == "__main__":
    app.add_routes(routes)
    paths = []
    log.debug("routes ", app.router.routes())

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(main())

    except KeyboardInterrupt:
        hs_init.log.info("Bye")
        exit(0)
