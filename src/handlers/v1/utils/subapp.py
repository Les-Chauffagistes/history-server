from aiohttp import web
from init import log

v1 = web.Application()
log.debug("app v1 created")
routes = web.RouteTableDef()

log.debug("Importing routes")
from ..import stats, weights, health
log.debug("Routes imported")
log.debug("done. Adding routes")
v1.add_routes(routes)
log.debug("routes added")
