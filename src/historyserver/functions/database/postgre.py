import os
import asyncpg
from dotenv import load_dotenv

load_dotenv(".env")

class Postgre:    
    @classmethod
    async def get_connection(cls, databse: str) -> asyncpg.Connection:
        _password = os.getenv("POSTGRE_PASSWORD")
        assert _password is not None
        return await asyncpg.connect(
            host="192.168.1.201",
            port=5432,
            user="postgres",
            password=_password,
            database=databse,
        )