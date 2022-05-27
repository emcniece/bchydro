import os
import asyncio
from bchydro import BCHydroApi

LOGLEVEL = os.environ.get('LOGLEVEL', 'WARNING').upper()
logging.basicConfig(level=LOGLEVEL)
logger = logging.getLogger(__name__)

async def main():
    a = BCHydroApi(os.environ.get("BCH_USER"), os.environ.get("BCH_PASS"), cache_ttl=10)
    usage = await a.get_usage(hourly=False)
    print(usage)

    print("Latest point:", await a.get_latest_point())
    print("Latest interval:", await a.get_latest_interval())
    print("Latest usage:", await a.get_latest_usage())
    print("Latest cost:", await a.get_latest_cost())


asyncio.run(main())
