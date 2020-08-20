# BCHydro API

![PyPi publish](https://github.com/emcniece/bchydro/workflows/Publish%20PyPi/badge.svg)

BCHydro Python API for extracting electricity usage statistics from your personal account.

## Installation

Via [PyPi](https://pypi.org/project/bchydro/):

```sh
pip install bchydro
```

Via Github:

```sh
git clone https://github.com/emcniece/bchydro.git
cd bchydro
pip install -r requirements.txt
```

## Usage

Running the example script:

```sh
pip install bchydro

export BCH_USER=your.email@domain.com
export BCH_PASS=your-bch-password

python test.py
```

Using in a project:

```py
import asyncio
from bchydro import BCHydroApi

async def main():
    a = BCHydroApi()
    await a.authenticate("username", "password")

    usage = await a.get_daily_usage()
    print(usage.electricity)
    print(a.get_latest_point())
    print(a.get_latest_usage())
    print(a.get_latest_cost())

asyncio.run(main())
```


## Todo

- [ ] Tests
- [ ] Publish on release, not tag
