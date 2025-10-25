import asyncio
import logging
from aiohttp import web
from .crawlers.stats import gather_stats
from .init import app, routes, log, port
from .cors import cors
print = log.info

async def start_background_tasks(app):
    tasks = [
        gather_stats(),
    ]
    await asyncio.gather(
        *tasks
    )
    
app.on_startup.append(start_background_tasks)

if __name__ == '__main__':
    logging.basicConfig(level = None, stream = None)
    app.add_routes(routes)
    paths = []
    for route in app.router.routes():
        if route.handler.__name__.startswith("public"):
            log.info("added cors on", route)
            cors.add(route)
    

    web.run_app(app, port=port, host = '0.0.0.0')