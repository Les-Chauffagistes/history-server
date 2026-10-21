import asyncio
import signal

from src.utils.cors import cors
import init as hs_init
from init import routes, app, log
from aiohttp import web
from src.crawlers.stats import gather_stats
from src.settings import settings
import src.core


SHUTDOWN_TIMEOUT = 20


async def main():
    hs_init.log.info("Démarrage du serveur...")
    stop = asyncio.Event()
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, stop.set)

    runner = web.AppRunner(app, shutdown_timeout=SHUTDOWN_TIMEOUT)
    crawler: asyncio.Task | None = None
    try:
        await runner.setup()
        if settings.port:
            site = web.TCPSite(runner, '0.0.0.0', settings.port)
            await site.start()
        hs_init.log.info(f'Serveur interne en ligne sur localhost:{settings.port}')
        if settings.gather_stats:
            crawler = asyncio.create_task(gather_stats(), name="gather_stats")
        await stop.wait()
        hs_init.log.info("Signal d'arrêt reçu, arrêt en cours...")
    finally:
        if crawler:
            crawler.cancel()
            await asyncio.gather(crawler, return_exceptions=True)
        # arrête le listener, attend les requêtes en cours puis exécute on_cleanup (fermeture du pool DB)
        await runner.cleanup()
        hs_init.log.info("Bye")

if __name__ == "__main__":
    app.add_routes(routes)
    paths = []
    log.debug(f"routes {app.router.routes()}")
    for route in app.router.routes():
        log.info(f"added cors on {route}")
        cors.add(route)

    asyncio.run(main())
