import os
import asyncio

from bchydro import BCHydroApi

async def main():
    a = BCHydroApi(os.environ.get("BCH_USER"), os.environ.get("BCH_PASS"))
    await a.authenticate()
    usage = await a.get_usage(hourly=False)
    print(usage.electricity)
    print(a.get_latest_point())
    print(a.get_latest_interval().start, a.get_latest_interval().end)
    print(a.get_latest_usage())
    print(a.get_latest_cost())


asyncio.run(main())
