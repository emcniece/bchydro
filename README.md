# BCHydro API

![PyPi publish](https://github.com/emcniece/bchydro/workflows/Publish%20PyPi/badge.svg)

BCHydro Python API for extracting electricity usage statistics from your personal account.

## Usage

```sh
export BCH_USER=your.email@domain.com
export BCH_PASS=your-bch-password
python test.py
```

## Release

```sh
python setup.py sdist
twine upload dist/*
```

## Todo

- Think about how bad it is to have rates & account inside `BCHydroDailyUsage`. Did this to get data out to HASS faster...
