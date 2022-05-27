import os
import asyncio
from bchydro import BCHydroApi2
import logging

async def main():
    a = BCHydroApi2(os.environ.get("BCH_USER"), os.environ.get("BCH_PASS"))
    usage = await a.get_usage(hourly=False)
    print(usage)


    # print("Latest point:", await a.get_latest_point())
    # print("Latest interval:", await a.get_latest_interval())
    # print("Latest usage:", await a.get_latest_usage())
    # print("Latest cost:", await a.get_latest_cost())

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
