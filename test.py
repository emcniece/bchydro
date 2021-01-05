import os
import asyncio
import time
from bchydro import BCHydroApi


async def main():
    a = BCHydroApi(os.environ.get("BCH_USER"), os.environ.get("BCH_PASS"), cache_ttl=10)
    # usage = await a.get_usage(hourly=False)
    print(await a.get_usage())
    print(await a.get_latest_point())
    print(await a.get_latest_interval())
    print(await a.get_latest_usage())
    print(await a.get_latest_cost())


asyncio.run(main())
