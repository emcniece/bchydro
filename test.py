import os
import asyncio

from bchydro import BCHydroApi

a = BCHydroApi()


async def main():
    await a.authenticate(os.environ.get("BCH_USER"), os.environ.get("BCH_PASS"))

    usage = await a.get_usage(hourly=False)
    for data in usage.electricity:
        print (data.interval.start, data.interval.end, data.cost, data.consumption)

    print(a.get_latest_point())
    print(a.get_latest_interval().start, a.get_latest_interval().end)
    print(a.get_latest_usage())
    print(a.get_latest_cost())


asyncio.run(main())
