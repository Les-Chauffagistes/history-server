import aiohttp_cors
from historyserver.init import app

cors = aiohttp_cors.setup(
    app,
    defaults={
        "https://stats.chauffagistes-pool.fr": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*"
        ),
        "http://localhost:8091": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*"
        )
    }
)