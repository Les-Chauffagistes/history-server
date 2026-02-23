import asyncio

from utils.cors import cors
import init as hs_init
from init import MODE, routes, PORT, app, log
from aiohttp import web
from crawlers.stats import gather_stats
import core


async def main():
    hs_init.log.info("Démarrage du serveur...")
    runner = web.AppRunner(app)
    await runner.setup()
    if PORT:
        site = web.TCPSite(runner, '0.0.0.0', PORT)
        await site.start()
    hs_init.log.info(f'Serveur interne en ligne sur localhost:{PORT}')
    if MODE == "PROD":
        await gather_stats()
    while True:
        await asyncio.sleep(1)

if __name__ == "__main__":
    app.add_routes(routes)
    paths = []
    log.debug("routes ", app.router.routes())
    for route in app.router.routes():
        log.info("added cors on", route)
        cors.add(route)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(main())

    except KeyboardInterrupt:
        hs_init.log.info("Bye")
        exit(0)
