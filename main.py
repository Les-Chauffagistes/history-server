import asyncio
import signal

from src.utils.cors import cors
import init as hs_init
from init import routes, app, log
from aiohttp import web
from chauff_cmn.callers.pools import PoolAPIClient
from src.crawlers.stats import gather_stats
from src.settings import settings
import src.core


SHUTDOWN_TIMEOUT = 20


def _watch_crawler(stop: asyncio.Event):
    def on_done(task: asyncio.Task) -> None:
        if task.cancelled():
            return
        exc = task.exception()
        # le crawler est censé tourner indéfiniment : toute fin est anormale, on arrête le process
        log.error("gather_stats s'est arrêté de façon inattendue", exc_info=exc)
        stop.set()
    return on_done


async def main():
    hs_init.log.info("Démarrage du serveur...")
    stop = asyncio.Event()
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, stop.set)

    runner = web.AppRunner(app, shutdown_timeout=SHUTDOWN_TIMEOUT)
    crawler: asyncio.Task | None = None
    client: PoolAPIClient | None = None
    try:
        await runner.setup()
        if settings.port:
            site = web.TCPSite(runner, '0.0.0.0', settings.port)
            await site.start()
        hs_init.log.info(f'Serveur interne en ligne sur localhost:{settings.port}')
        if settings.gather_stats:
            log.info("Stats will be collected")
            # construit hors de la tâche : une erreur de config fait échouer le démarrage
            client = PoolAPIClient(api_url=settings.stats_url, api_key=settings.stats_api_token)
            crawler = asyncio.create_task(gather_stats(client), name="gather_stats")
            crawler.add_done_callback(_watch_crawler(stop))
        else:
            log.info("Stats will not be collected")
        await stop.wait()
        hs_init.log.info("Signal d'arrêt reçu, arrêt en cours...")
    finally:
        if crawler:
            crawler.cancel()
            await asyncio.gather(crawler, return_exceptions=True)
        if client:
            await client.close()
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
