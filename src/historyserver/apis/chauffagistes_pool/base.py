from ...apis.utils import make_request

BASE_URL = "https://chauffagistes-pool.fr:3000/api/"

async def send_request(path: str):
    return await make_request(BASE_URL, path)