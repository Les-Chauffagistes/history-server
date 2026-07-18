from src.core.services.health.v1.helath import check_health
from .utils.subapp import routes
from aiohttp.web_request import Request
from aiohttp.web_response import json_response

@routes.get("/health")
async def health(request: Request):
    return json_response({"status": await check_health()})