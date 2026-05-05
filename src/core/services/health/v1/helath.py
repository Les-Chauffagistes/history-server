from src.database.postgre import POOL


async def check_health() -> bool:
    try:
        await POOL.get().execute("SELECT 1")
        return True
    
    except Exception:
        return False