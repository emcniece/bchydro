import aiohttp
import logging
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup

from .types import (
    BCHydroAccount,
    BCHydroInterval,
    BCHydroRates,
    BCHydroDailyElectricity,
    BCHydroDailyUsage,
)

from .const import (
    USER_AGENT,
    URL_POST_LOGIN,
    URL_GET_ACCOUNTS,
    URL_ACCOUNTS_OVERVIEW,
    URL_GET_ACCOUNT_JSON,
    URL_POST_CONSUMPTION_XML,
)

_LOGGER = logging.getLogger(__name__)


class BCHydroApi:
    def __init__(self, username, password):
        """Initialize the sensor."""
        self._username = username
        self._password = password
        self._cookie_jar = None
        self._bchydroparam = None
        self.account: BCHydroAccount = None
        self.usage: BCHydroDailyUsage = None
        self.rates: BCHydroRates = None

    async def authenticate(self) -> bool:
        async with aiohttp.ClientSession(headers={"User-Agent": USER_AGENT}) as session:
            response = await session.post(
                URL_POST_LOGIN,
                data={
                    "realm": "bch-ps",
                    "email": self._username,
                    "password": self._password,
                    "gotoUrl": "https://app.bchydro.com:443/BCHCustomerPortal/web/login.html",
                },
            )
            response.raise_for_status()
            _LOGGER.debug('history:', response.history)

            if response.status != 200:
                return False

            self._cookie_jar = session.cookie_jar

            # Extract hydroparam from page HTML for use in the consumption endpoint.
            # The param appears twice: a hidden <input /> and a span with an id.
            page_html = await response.text()

            try:
                soup = BeautifulSoup(page_html, features="html.parser")
                self._bchydroparam = self.parse_bchydroparam(soup)

                # If the user has multiple accounts (eg. after a move), pick the first open one
                # todo: allow user to specify
                account_list_divs = soup.find_all("div", class_="accountListDiv")
                if len(account_list_divs) > 0:
                    accounts_response = await session.post(URL_GET_ACCOUNTS, headers={'x-csrf-token': self._bchydroparam})
                    accounts = await accounts_response.json()
                    account_id = accounts['accounts'][0]['accountId']
                    response = await session.get(URL_ACCOUNTS_OVERVIEW + "?aid=" + account_id)
                    page_html = await response.text()
                    soup = BeautifulSoup(page_html, features="html.parser")
                    self._bchydroparam = self.parse_bchydroparam(soup)

            except AttributeError:
                _LOGGER.error(
                    "Login failed - unable to find bchydroparam. Are your credentials set?"
                )
                raise

            alert_errors = soup.find(True, {'class': ['alert', 'error']})
            if alert_errors:
                raise Exception("Detected login page error(s): " + alert_errors.text)

            try:
                response = await session.get(URL_GET_ACCOUNT_JSON)
                json_res = await response.json()

                self.account = BCHydroAccount(
                    json_res["evpSlid"],
                    json_res["evpAccount"],
                    json_res["evpAccountId"],
                    json_res["evpProfileId"],
                    json_res["evpRateGroup"],
                    json_res["evpBillingStart"],
                    json_res["evpBillingEnd"],
                    json_res["evpConsToDate"],
                    json_res["evpCostToDate"],
                    json_res["yesterdayPercentage"],
                    json_res["evpEstConsCurPeriod"],
                    json_res["evpEstCostCurPeriod"],
                    json_res["evpCurrentDateTime"],
                )

            except Exception as e:
                _LOGGER.debug("Auth response text: %s", await response.text())
                _LOGGER.error("Auth error: %s", e)
                return False

        return True

    def parse_bchydroparam(self, soup: BeautifulSoup) -> str:
        span_element = soup.find(id="bchydroparam")
        if span_element:
            return span_element.text
        input_element = soup.find('input', {'name': "bchydroparam"})
        if input_element:
            return input_element.get('value')
        raise Exception('Unable to find bchydroparam; likely failed to login')

    async def get_daily_usage(self) -> BCHydroDailyUsage:
        return await self.get_usage(hourly=False)

    async def get_usage(self, hourly = False) -> BCHydroDailyUsage:
        if not self.account:
            _LOGGER.error("Unauthenticated")
            raise Exception("Unauthenticated")

        async with aiohttp.ClientSession(
            cookie_jar=self._cookie_jar, headers={"User-Agent": USER_AGENT}
        ) as session:
            response = await session.post(
                URL_POST_CONSUMPTION_XML,
                data={
                    "Slid": self.account.evpSlid,
                    "Account": self.account.evpAccount,
                    "ChartType": "column",
                    "Granularity": hourly and "hourly" or "daily",
                    "Overlays": "none",
                    "DateRange": "currentBill",
                    "StartDateTime": self.account.evpBillingStart,
                    "EndDateTime": self.account.evpBillingEnd,
                    "RateGroup": self.account.evpRateGroup,
                },
                headers={"bchydroparam": self._bchydroparam},
            )

            try:
                text = await response.text()
                root = ET.fromstring(text)
                new_usage: BCHydroDailyUsage = []

                for point in root.findall("Series")[0].findall("Point"):
                    # For now we're hard-filtering ACTUAL datapoints.
                    # It might be worth looking into ESTIMATED points...
                    # This renders self.is_valid() redundant.
                    if point.get("quality") != "ACTUAL":
                        continue

                    interval = BCHydroInterval(
                        point.get("dateTime"), point.get("endTime")
                    )

                    new_usage.append(
                        BCHydroDailyElectricity(
                            type=point.get("type"),
                            quality=point.get("quality"),
                            consumption=point.get("value"),
                            interval=interval,
                            cost=point.get("cost"),
                        )
                    )

                rates = root.find("Rates")
                self.rates = BCHydroRates(
                    rates.get("daysSince"),
                    rates.get("cons2date"),
                    rates.get("cost2date"),
                    rates.get("estCons"),
                    rates.get("estCost"),
                )

                self.usage = BCHydroDailyUsage(
                    electricity=new_usage, rates=self.rates, account=self.account
                )

            except ET.ParseError as e:
                _LOGGER.error("Unable to parse XML from string: %s -- %s", e, text)
                raise
            except Exception as e:
                _LOGGER.error("Unexpected error: %s", e)
                raise

        return self.usage

    def is_valid(self, point):
        return point.quality == "ACTUAL"

    def get_latest_point(self) -> BCHydroDailyElectricity:
        if not self.account:
            _LOGGER.error("Unauthenticated")
            return

        valid = list(filter(self.is_valid, self.usage.electricity))
        return valid[-1] if len(valid) else None

    def get_latest_interval(self) -> BCHydroInterval:
        if not self.account:
            _LOGGER.error("Unauthenticated")
            return

        valid = list(filter(self.is_valid, self.usage.electricity))
        return valid[-1].interval if len(valid) else None

    def get_latest_usage(self):
        if not self.account:
            _LOGGER.error("Unauthenticated")
            return

        valid = list(filter(self.is_valid, self.usage.electricity))
        return valid[-1].consumption if len(valid) else None

    def get_latest_cost(self):
        if not self.account:
            _LOGGER.error("Unauthenticated")
            return

        valid = list(filter(self.is_valid, self.usage.electricity))
        return valid[-1].cost if len(valid) else None
