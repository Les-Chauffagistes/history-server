import os
import asyncpg
from dotenv import load_dotenv

load_dotenv(".env")

class Postgre:    
    @classmethod
    async def get_connection(cls, databse: str) -> asyncpg.Connection:
        _password = os.getenv("POSTGRE_PASSWORD")
        _host = os.getenv("POSTGRE_HOST")
        _port = os.getenv("POSTGRE_PORT")
        _user = os.getenv("POSTGRE_USER")
        assert _password is not None
        return await asyncpg.connect(
            host=_host,
            port=_port,
            user=_user,
            password=_password,
            database=databse,
        )