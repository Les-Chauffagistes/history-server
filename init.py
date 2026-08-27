from aiohttp import web
from typing import cast
from os import getenv
from dotenv import load_dotenv
from pathlib import Path
from chauff_cmn.logging import configure, logger as log
from src.database.postgre import close_db_pool, create_db_pool
from src.middlewares.logger import error_handler

ROOT_DIR = Path(__file__).resolve().parents[0]
load_dotenv(ROOT_DIR / ".env", override=True)
configure(service="history-server", level=getenv("LOG_LEVEL", "DEBUG"))

app = web.Application(middlewares=(error_handler,))
app.on_startup.append(create_db_pool)
app.on_cleanup.append(close_db_pool)
routes = web.RouteTableDef()

GATHER_STATS = getenv("GATHER_STATS", "true").lower() == "true"
PORT = cast(int, getenv("PORT"))