#import sys
#import aiohttp
import logging
# from datetime import datetime, timedelta
# import xml.etree.ElementTree as ET
# from bs4 import BeautifulSoup
# from ratelimit import limits
# from tenacity import (
#     retry,
#     stop_after_attempt,
#     retry_if_exception_type,
#     wait_fixed,
#     TryAgain,
# )

import asyncio
from pyppeteer import launch
import time
import os
import xml.etree.ElementTree as ET


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
    BCHydroInvalidXmlException,
    BCHydroAlertDialogException,
    BCHydroInvalidDataException,
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

    URL_LOGIN_PAGE,
)

from .util import parse_consumption_xml

LOGLEVEL = os.environ.get('LOGLEVEL', 'WARNING').upper()
#logging.basicConfig(level=LOGLEVEL)
logger = logging.getLogger(__name__)
logger.setLevel(LOGLEVEL)


class BCHydroApi2:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.slid = None
        self.accountNumber = None
        
    def _authenticated(func):
        async def wrapper(self, *args, **kwargs):
            if not (self.slid and self.page):
                await self.authenticate()
            await func(self, *args, **kwargs)
        return wrapper

    async def authenticate(self):
        self.browser = await launch(slowMo=False, autoclose=True, devtools=False)
        self.page = await self.browser.newPage()

        logger.debug('Populating login form...')
        await self.page.goto(URL_LOGIN_PAGE)
        await self.page.waitForSelector('#email')
        await self.page.type('#email', self.username)
        await self.page.type('#password', self.password)

        logger.debug('Clicking login button...')
        await asyncio.gather(
            self.page.waitForNavigation(),
            self.page.click('#submit-button'),
        )

        logger.debug('Extracting account numbers...')
        self.slid = await self.page.evaluate("input_slid")
        self.accountNumber = await self.page.evaluate("input_accountNumber")


    @_authenticated
    async def get_accounts(self):
        eval_js = f"""
        async()=>{{
            const res = await fetch(
                '{url}',
                {{
                    method: 'POST',
                    headers: {{
                        'Content-Type':'application/x-www-form-urlencoded',
                        'bchydroparam':'{bchp}',
                        'x-csrf-token':'{bchp}',
                    }}
                }}
            );
            const text = await res.text();
            return text;
        }}
        """

    @_authenticated
    async def get_usage(self, hourly=False):
        # Navigate to Consumption page by clicking button:
        logger.debug('Clicking Detailed Consumption button...')
        await self.page.waitForSelector('#detailCon:not([disabled])')
        await asyncio.gather(
            self.page.waitForNavigation(),
            self.page.click('#detailCon'),
        )

        # Evaluate JS fetch() request in DOM
        logger.debug('Extracting bchydroparam...')
        bchp = await self.page.evaluate("document.querySelector('span#bchydroparam').innerText")
        url="https://app.bchydro.com/evportlet/web/consumption-data.html"

        logger.debug('Making fetch() request...')
        postdata = f'Slid={self.slid}&Account={self.accountNumber}&ChartType=column&Granularity=daily&Overlays=none&StartDateTime=2022-04-07T00%3A00%3A00-07%3A00&EndDateTime=2022-06-07T00%3A00%3A00-07%3A00&DateRange=currentBill&RateGroup=RES1'
        eval_js = f"""
        async()=>{{
            const res = await fetch(
                '{url}',
                {{
                    method: 'POST',
                    headers: {{
                        'Content-Type':'application/x-www-form-urlencoded',
                        'bchydroparam':'{bchp}',
                        'x-csrf-token':'{bchp}',
                    }},
                    body: '{postdata}'
                }}
            );
            const text = await res.text();
            return text;
        }}
        """

        xml = await self.page.evaluate(eval_js)
        usage, rates = parse_consumption_xml(xml)
        return usage, rates
