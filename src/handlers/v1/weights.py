from handlers.v1.utils.parsers import parse_workers_weight
from handlers.v1.utils.serializers import serialyze_worker_weights
from .utils.subapp import routes
from core.services.weights.v1 import weights
from aiohttp.web_request import Request
from aiohttp.web import json_response

@routes.get("/{address}/weights")
async def get_workers_weights(request: Request):
    data = await weights.get_workers_weight(parse_workers_weight(request))
    return json_response(list(serialyze_worker_weights(data)))