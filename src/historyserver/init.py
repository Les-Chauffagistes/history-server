import traceback
from aiohttp import web, web_exceptions
from aiohttp.web import middleware
from aiohttp.web_request import Request
from aiohttp.web import StreamResponse, json_response
from typing import Awaitable, Callable, Literal, cast
from aiohttp.web import Request
from .modules.logger.logger import Logger
from os import getenv
from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]

load_dotenv(ROOT_DIR / ".env")

log = Logger("log.log")
print = log.info

@middleware
async def error_handler(request: Request, handler: Callable[[Request], Awaitable[StreamResponse]]) -> StreamResponse:
    method = request.method
    match method:
        case "GET":
            line = log.get(request.path)
        
        case "POST":
            line = log.post(request.path)
        
        case "DELETE":
            line = log.delete(request.path)
        
        case _:
            line = log.info(request.path)
    
    assert line

    try:
        response = await handler(request)
        line.add_text(f"HTTP {response.status}")
        return response
    
    except Exception as e:
        if isinstance(e, web_exceptions.HTTPUnauthorized):
            line.add_text("HTTP 401")
            return json_response({"error": "Unauthorized"}, status = 401)

        elif isinstance(e, web_exceptions.HTTPNotFound):
            line.add_text("HTTP 404")
            return json_response({"error": "Not Found"}, status = 404)
    
        else:           
            line.add_text("HTTP 500")
            log.warn(traceback.format_exc())
            return json_response({"error": "Internal Server Error"}, status = 500)
    
    finally:
        line.edit_print()
        #log.warn(traceback.format_exc())

app = web.Application(
    middlewares = (error_handler,)
)
routes = web.RouteTableDef()
mode = cast(Literal["DEV", "PROD"], getenv("MODE"))
if mode == "DEV":
    port = 8051

else:
    port = 8050