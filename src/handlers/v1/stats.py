from aiohttp.web_request import Request
from aiohttp.web import json_response

from core.services.stats.v1 import stats
from .utils.parsers import parse_pool_last_n, parse_pool_stats, parse_worker_last_n, parse_worker_stats
from .utils.serializers import serialize_worker_stats, serialze_pool_stats, serialze_pool_stats_last_n

from init import log
from .utils.subapp import routes

log.info("Added route Stats")


@routes.get("/{address}/worker/{workername}/{period}")
async def get_worker_stats(request: Request):
    data = await stats.get_worker_stats(parse_worker_stats(request))
    return json_response(list(serialize_worker_stats(data)))

@routes.get("/{address}/pool")
async def get_pool_stats(request: Request):
    data = await stats.get_pool_stats(parse_pool_stats(request))
    return json_response(list(serialze_pool_stats(data)))

@routes.get("/{address}/worker/{workername}/{source}/last/{n}")
async def get_worker_stats_last_n(request: Request):
    data = await stats.get_worker_stats_last_n(parse_worker_last_n(request))
    return json_response(list(serialize_worker_stats(data)))

@routes.get("/{address}/pool/{source}/last/{n}")
async def get_pool_stats_last_n(request: Request):
    data = await stats.get_pool_stats_last_n(parse_pool_last_n(request))
    return json_response(list(serialze_pool_stats_last_n(data)))