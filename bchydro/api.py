import aiohttp
import logging
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from ratelimit import limits
from tenacity import retry, stop_after_attempt, wait_fixed, TryAgain

from .types import (
    BCHydroAccount,
    BCHydroInterval,
    BCHydroRates,
    BCHydroDailyElectricity,
    BCHydroDailyUsage,
)

from .exceptions import (
    BCHydroAuthException,
    BCHydroParamException,
    BCHydroInvalidHtmlException,
    BCHydroInvalidXmlException,
    BCHydroAlertDialogException,
)

from .const import (
    FIVE_MINUTES,
    USER_AGENT,
    URL_POST_LOGIN,
    URL_LOGIN_GOTO,
    URL_GET_ACCOUNTS,
    URL_ACCOUNTS_OVERVIEW,
    URL_GET_ACCOUNT_JSON,
    URL_POST_CONSUMPTION_XML,
)

# logging.basicConfig(level=logging.DEBUG)
_LOGGER = logging.getLogger(__name__)


class BCHydroApi:
    def __init__(self, username, password, cache_ttl=FIVE_MINUTES):
        """Initialize the sensor."""
        self._username = username
        self._password = password
        self._cookie_jar = None
        self._bchydroparam = None
        self._cache_ttl = cache_ttl
        self._cache_expiration_time = None
        self.account: BCHydroAccount = None
        self.usage: BCHydroDailyUsage = None
        self.rates: BCHydroRates = None
        self.latest_point: BCHydroDailyElectricity = None
        self.latest_interval: BCHydroInterval = None
        self.latest_usage: BCHydroDailyUsage = None
        self.latest_cost = None

    def _parse_bchydroparam(self, soup: BeautifulSoup) -> str:
        """
        Extract bchydroparam from page HTML for use in the consumption endpoint.
        The param often appears twice: a hidden <input /> and a <span /> with an id.
        The <input /> element appears more reliably than the <span /> so we use the input.
        This seems to be a CSRF token, though it isn't confirmed as such.
        """
        span_element = soup.find(id="bchydroparam")
        if span_element:
            return span_element.text
        input_element = soup.find("input", {"name": "bchydroparam"})
        if input_element:
            return input_element.get("value")
        raise BCHydroParamException(
            "Unable to find bchydroparam; likely failed to login"
        )

    def _validate_html_response(self, html) -> BeautifulSoup:
        soup = None
        alert_errors = None

        try:
            soup = BeautifulSoup(html, features="html.parser")
            alert_errors = soup.find(True, {"class": ["alert", "error"]})
            self._bchydroparam = self._parse_bchydroparam(soup)
        except:
            raise BCHydroInvalidHtmlException()

        if alert_errors:
            raise BCHydroAlertDialogException(alert_errors.text)

        return soup

    def _bust_cache(self):
        self._cache_expiration_time = datetime.now() + timedelta(
            seconds=self._cache_ttl
        )

    def _is_cache_expired(self):
        if self._cache_expiration_time is not None:
            expired = datetime.now() > self._cache_expiration_time
        else:
            expired = True
        return expired

    async def _auth_again_if(self, condition, debug_msg=None):
        if condition:
            if debug_msg is not None:
                _LOGGER.debug(debug_msg)
            await self._authenticate()
            raise TryAgain

    async def _refresh_if(self, condition, debug_msg=None):
        if condition:
            if debug_msg is not None:
                _LOGGER.debug(debug_msg)

            await self.refresh()
            raise TryAgain

    @limits(calls=5, period=FIVE_MINUTES)
    async def _authenticate(self) -> bool:
        _LOGGER.debug("authenticating with username: %s", self._username)

        async with aiohttp.ClientSession(headers={"User-Agent": USER_AGENT}) as session:
            response = await session.post(
                URL_POST_LOGIN,
                data={
                    "realm": "bch-ps",
                    "email": self._username,
                    "password": self._password,
                    "gotoUrl": URL_LOGIN_GOTO,
                },
            )
            if response.status != 200:
                raise BCHydroAuthException()

            self._cookie_jar = session.cookie_jar
            page_html = await response.text()
            soup = self._validate_html_response(page_html)

            # If the user has multiple accounts (eg. after a move), pick the first open one
            # todo: allow user to specify
            account_list_divs = soup.find_all("div", class_="accountListDiv")
            if len(account_list_divs) > 0:
                accounts_response = await session.post(
                    URL_GET_ACCOUNTS, headers={"x-csrf-token": self._bchydroparam}
                )
                accounts = await accounts_response.json()
                account_id = accounts["accounts"][0]["accountId"]
                response = await session.get(
                    URL_ACCOUNTS_OVERVIEW + "?aid=" + account_id
                )
                page_html = await response.text()
                self._validate_html_response(page_html)

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
                raise BCHydroAuthException(e)

        return True

    @retry(stop=stop_after_attempt(2), wait=wait_fixed(1))
    async def refresh(self, hourly=False) -> BCHydroDailyUsage:
        if not self._is_cache_expired():
            _LOGGER.debug("Returning cached usage")
            return self.usage

        if not self.account:
            await self._authenticate()

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

            await self._auth_again_if(
                condition=str(response.url) != str(URL_POST_CONSUMPTION_XML),
                debug_msg="Unexpected XML URL, has session expired?",
            )

            await self._auth_again_if(
                condition="application/xml" not in response.headers["content-type"],
                debug_msg="Unexpected XML content-type, has session expired?",
            )

            try:
                text = await response.text()
                root = ET.fromstring(text)
            except ET.ParseError as e:
                raise BCHydroInvalidXmlException(e)

            new_usage: BCHydroDailyUsage = []

            try:
                for point in root.findall("Series")[0].findall("Point"):
                    # For now we're hard-filtering ACTUAL datapoints.
                    # It might be worth looking into ESTIMATED points...
                    # This renders self._is_valid_point() redundant.
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
            except Exception as e:
                raise BCHydroInvalidDataException(e)

            self.rates = BCHydroRates(
                rates.get("daysSince"),
                rates.get("cons2date"),
                rates.get("cost2date"),
                rates.get("estCons"),
                rates.get("estCost"),
            )

            usage = BCHydroDailyUsage(
                electricity=new_usage, rates=self.rates, account=self.account
            )

            self._bust_cache()
            self._set_usage(usage)
            self._set_latest_point(usage)
            self._set_latest_interval(usage)
            self._set_latest_usage(usage)
            self._set_latest_cost(usage)

        return self.usage

    def _is_valid_point(self, point):
        return point.quality == "ACTUAL"

    def _set_usage(self, usage):
        self.usage = usage

    @retry(stop=stop_after_attempt(2))
    async def get_usage(self) -> BCHydroDailyUsage:
        await self._refresh_if(not self.usage)
        return self.usage

    def _set_latest_point(self, usage):
        valid_point = list(filter(self._is_valid_point, self.usage.electricity))
        self.latest_point = valid_point[-1] if len(valid_point) else None

    @retry(stop=stop_after_attempt(2))
    async def get_latest_point(self) -> BCHydroDailyElectricity:
        await self._refresh_if(not self.latest_point)
        return self.latest_point

    def _set_latest_interval(self, usage):
        valid_point = list(filter(self._is_valid_point, self.usage.electricity))
        self.latest_interval = valid_point[-1].interval if len(valid_point) else None

    @retry(stop=stop_after_attempt(2))
    async def get_latest_interval(self) -> BCHydroInterval:
        await self._refresh_if(not self.latest_interval)
        return self.latest_interval

    def _set_latest_usage(self, usage):
        valid_point = list(filter(self._is_valid_point, self.usage.electricity))
        self.latest_usage = valid_point[-1].consumption if len(valid_point) else None

    @retry(stop=stop_after_attempt(2))
    async def get_latest_usage(self):
        await self._refresh_if(not self.latest_usage)
        return self.latest_usage

    def _set_latest_cost(self, usage):
        valid_point = list(filter(self._is_valid_point, self.usage.electricity))
        self.latest_cost = valid_point[-1].cost if len(valid_point) else None

    @retry(stop=stop_after_attempt(2))
    async def get_latest_cost(self):
        await self._refresh_if(not self.latest_cost)
        return self.latest_cost
