from ...models.APIData import APIPayload
from .base import send_request


    
async def get_every_user_data() -> APIPayload:
    return await send_request("data")
