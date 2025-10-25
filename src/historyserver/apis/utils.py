import os
from aiohttp import ClientSession
from dotenv import load_dotenv
from historyserver.init import log
load_dotenv("./env")

async def make_request(base: str, path: str):
    line = log.info(f"Performing request {base}{path}")
    token = os.getenv("STATS_API_TOKEN")
    assert token
    async with ClientSession(base, headers={"Authorization": "Bearer " + token}) as session:
        async with session.get(path) as response:
            line.add_text("HTTP", response.status)
            line.edit_print()
            return await response.json()