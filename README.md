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

    usage = await a.get_usage(hourly=False)
    print(usage.electricity)
    print(a.get_latest_point())
    print(a.get_latest_usage())
    print(a.get_latest_cost())

asyncio.run(main())
```

BCHydro offers [view-only accounts](https://app.bchydro.com/BCHCustomerPortal/web/accountAccessView.html),
as a more secure option.

## Todo

- [ ] Tests
- [ ] Publish on release, not tag
- [ ] Handle account locking?
    ```html
    <div id="alertMessage" class="alert error"><h3 class="icon">Sorry, your account is locked</h3></div>
    <div>
        <p>To ensure your account security, we've locked your account to prevent further attempts to log in.</p>
        <p>You may try again after 5 minutes, or contact Customer Service.</p>
        <p>
            <a name="resetPassword" class="primary button" href="/BCHCustomerPortal/forgotPassword.html">Reset password</a>
            <a name="returnToLogin" class="secondary button" href="/BCHCustomerPortal/web/login.html">Return to login</a>
        </p>
    </div>
    </div>

    </div>
    ```

## Disclaimer

This package has been developed without the express permission of BC Hydro. It accesses data by submitting forms that end-users would typically use in a browser. I'd love to work with BC Hydro to find a better way to access this data, perhaps through an official API... if you know anyone that works there, pass this along!
