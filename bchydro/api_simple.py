import asyncio
import logging
import os
from datetime import datetime
from typing import Optional

from bs4 import BeautifulSoup
from pyppeteer import launch

from .const import URL_LOGIN_PAGE

LOGLEVEL = os.environ.get("LOGLEVEL", "WARNING").upper()
logger = logging.getLogger(__name__)
logger.setLevel(LOGLEVEL)


class BCHydroApiSimple:
    def __init__(
        self, username: str, password: str, browser_exec_path: Optional[str] = None
    ):
        """BC Hydro data accessor through headless browser.

        *Note* that username and password are stored in the object.
        Be sure you trust the environment where this object is created and instance is executed.

        Reduce your risks by creating a read-only BCHydro account following
        https://github.com/emcniece/bchydro?tab=readme-ov-file#-read-only-account-sharing.

        Args:
            username (str): BCHydro username
            password (str): BCHydro password
            browser_exec_path (str): Path to browser executabble. Useful if browser is not in PATH.

        """
        self.page = None
        self._username = username
        self._password = password
        self.browser_exec_path = browser_exec_path

    async def _sign_in(self, username, password, browser_exec_path):
        browser = await launch(
            slowMo=True,
            autoclose=True,
            devtools=False,
            executablePath=browser_exec_path,
        )
        page = await browser.newPage()

        logger.debug("Populating login form...")
        await page.goto(URL_LOGIN_PAGE)
        await page.waitForSelector("#email")
        await page.type("#email", username)
        await page.type("#password", password)

        logger.debug("Clicking login button...")
        await asyncio.gather(
            page.waitForNavigation(),
            page.click("#submit-button"),
        )
        return page

    def _authenticated(func):
        async def wrapper(self, *args, **kwargs):
            if self.page is None:
                self.page = await self._sign_in(
                    self._username, self._password, self.browser_exec_path
                )
            await func(self, *args, **kwargs)

        return wrapper

    @_authenticated
    async def get_usage_table(self):
        # Navigate to Consumption page by clicking button:
        logger.debug("Clicking Detailed Consumption button...")
        await self.page.waitForSelector("#detailCon:not([disabled])")
        await asyncio.gather(
            self.page.waitForNavigation(),
            self.page.click("#detailCon"),
        )

        await self.page.screenshot({"path": "s_clickConsumption.png"})

        # Navigate to the table look
        logger.debug("Clicking Table button...")
        await self.page.waitForSelector("#tableBtnLabel")
        await self.page.click("#tableBtnLabel")
        await self.page.screenshot({"path": "s_afterBtn.png"})

        # Wait until the table with id="consumptionTable" is present
        await self.page.waitForSelector("table#consumptionTable")

        # Download the whole table at id="consumptionTable"
        html_table = await self.page.evaluate(
            "document.querySelector('table#consumptionTable').outerHTML"
        )
        with open("table.html", "w") as f:
            f.write(html_table)

        table = self.__parse_consumption_table(html_table)
        print("WIthin")
        print(table)

        return table

    def __parse_consumption_table(self, html_table: str):
        """Parse the consumption table from the HTML content.

        Converts <table>...</table> HTML content to a dictionary.
        It's expected that the table is a daily consumption with the day in the 'Date' column.
        Parsing converts Date into the key (`YYYY-MM-dd`) for the dictionary, and all columns are flatten into the dictionary per row.

        Args:
            html_table (str): HTML content of the table, i.e. <table>...</table>

        Returns:
            dict: Dictionary with the table data, where the keys are the date in short-ISO format (2024-09-01).

        """

        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(html_table, "html.parser")

        # Find the table element
        table = soup.find("table")

        # Extract table rows
        rows = table.find_all("tr")

        # Initialize the dictionary to store the table data
        table_dict = {}

        # Extract the header row to get the field names
        headers = [
            header.get_text(strip=True) for header in rows[0].find_all(["td", "th"])
        ]

        # Iterate over the rows and populate the dictionary
        for row in rows[1:]:  # Skip the header row
            cells = row.find_all(["td", "th"])
            cell_data = [cell.get_text(strip=True) for cell in cells]
            row_dict = dict(zip(headers, cell_data))

            date_key = row_dict.get("Date")
            if date_key:
                date_obj = datetime.strptime(date_key, "%b %d, %Y")
                formatted_date = date_obj.strftime("%Y-%m-%d")
                row_dict["Date"] = formatted_date
                table_dict[formatted_date] = row_dict

        return table_dict
