# BCHydro API

[![PyPi version](https://img.shields.io/pypi/v/bchydro?logo=pypi&logoColor=lightgrey)](https://pypi.org/project/bchydro/) ![Tested Python versions](https://img.shields.io/pypi/pyversions/bchydro?logo=python&logoColor=lightgrey) [![PyPi publish](https://github.com/emcniece/bchydro/workflows/Publish%20PyPi/badge.svg)](https://github.com/emcniece/bchydro/actions?query=workflow%3A%22Publish+PyPi%22?event=release) ![PyPi downloads](https://img.shields.io/pypi/dm/bchydro) ![Dependency updates](https://img.shields.io/librariesio/github/emcniece/bchydro)

BCHydro Python API for extracting electricity usage statistics from your personal account.

## Installation

Via [PyPi](https://pypi.org/project/bchydro/):

```sh
pip install bchydro
```

Via Github:

```sh
# Fetch the code
git clone https://github.com/emcniece/bchydro.git
cd bchydro

# Set up environment

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
    bch = BCHydroApi("username", "password")

    # Asynchronous usage:
    print(await bch.get_usage())
    print(await bch.get_latest_point())
    print(await bch.get_latest_usage())
    print(await bch.get_latest_interval())
    print(await bch.get_latest_cost())

    # Mostly synchronous usage:
    await bch.refresh()
    print(bch.usage)
    print(bch.latest_point)
    print(bch.latest_usage)
    print(bch.latest_interval)
    print(bch.latest_cost)

asyncio.run(main())
```

#### ⚠ Read-Only Account Sharing

This project accesses your BCHydro account as would a human in a browser. It is recommended that a read-only account is set up for use with this project for more secure operation. Using this secondary account also enables backup access in the event of account lockout.

- Instructions for adding read-only accounts can be [found here](https://www.bchydro.com/news/conservation/2014/myhydro-sharing-access.html).
- Read-only accounts can be [configured here](https://app.bchydro.com/BCHCustomerPortal/web/accountAccessView.html) after logging in.



## Version Publishing

This repo is automatically published to [PyPi](https://pypi.org/project/bchydro/) by means of a [Github Workflow](https://github.com/emcniece/bchydro/actions?query=workflow%3A%22Publish+PyPi%22) when a new [release](https://github.com/emcniece/bchydro/releases) is created on Github.


### Maintenance

Dependencies can be updated with [pip-tools](https://github.com/jazzband/pip-tools):

```sh
# Install pip-compile and pip-sync
pip install pip-tools

# Upgrade requirements
pip-compile --upgrade
```


## Todo

- [x] Publish on release, not tag
- [x] Handle account locking (looks for HTML alert dialogs)
- [ ] Unit tests
- [x] Automatic initial and re-authentication
- [x] Rate limiting, auth retries
- [ ] Exception documentation


## Disclaimer

This package has been developed without the express permission of BC Hydro. It accesses data by submitting forms that end-users would typically use in a browser. I'd love to work with BC Hydro to find a better way to access this data, perhaps through an official API... if you know anyone that works there, pass this along!
