from aiohttp import ClientSession


async def make_request(base: str, path: str, headers: dict[str, str]):
    # importer paresseusement le logger central pour éviter les importations circulaires
    import init as hs_init
    hs_init.log.info("Performing request", base, path)
    async with ClientSession(base, headers = headers) as session:
        async with session.get(path) as response:
            return await response.json()