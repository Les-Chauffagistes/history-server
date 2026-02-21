from aiohttp import web
from typing import Literal, cast
from os import getenv
from dotenv import load_dotenv
from pathlib import Path
from modules.logger import Logger
from database.postgre import close_db_pool, create_db_pool
from middlewares.logger import error_handler

ROOT_DIR = Path(__file__).resolve().parents[0]
load_dotenv(ROOT_DIR / ".env")
log = Logger("historyserver.log")

app = web.Application(middlewares=(error_handler,))
app.on_startup.append(create_db_pool)
app.on_cleanup.append(close_db_pool)
routes = web.RouteTableDef()
MODE = cast(Literal["DEV", "PROD"], getenv("MODE"))
if MODE == "DEV":
    PORT = 8051

else:
    PORT = 8050
