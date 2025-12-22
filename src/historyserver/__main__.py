import asyncio

from historyserver.crawlers.stats import gather_stats
from .init import log
print = log.info

if __name__ == '__main__':
    log.info("Starting history server...")
    asyncio.run(gather_stats())