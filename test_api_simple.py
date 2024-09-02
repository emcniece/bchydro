import argparse
import asyncio
import os

from bchydro import BCHydroApiSimple


async def main(bep=None):
    client = BCHydroApiSimple(
        os.environ.get("BCH_USER"), os.environ.get("BCH_PASS"), browser_exec_path=bep
    )
    usage = await client.get_usage_table()
    print(usage)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="BCHydro API")
    parser.add_argument("--bep", help="Path to browser executable path")
    args = parser.parse_args()

    asyncio.get_event_loop().run_until_complete(main(bep=args.bep))
