# BCHydro API

🚧 Under construction

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
