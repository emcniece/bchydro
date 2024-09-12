import xml.etree.ElementTree as ET

from .types import (
    #BCHydroAccount,
    BCHydroInterval,
    BCHydroRates,
    BCHydroDailyElectricity,
    BCHydroDailyUsage,
)

from .exceptions import (
    #BCHydroAuthException,
    #BCHydroParamException,
    BCHydroInvalidXmlException,
    #BCHydroAlertDialogException,
    BCHydroInvalidDataException,
)

def parse_consumption_xml(raw_xml):
    try:
        root = ET.fromstring(raw_xml)
    except ET.ParseError as e:
        raise BCHydroInvalidXmlException(e)

    usage: BCHydroDailyUsage = []

    try:
        for point in root.findall("Series")[0].findall("Point"):
            # For now we're hard-filtering ACTUAL datapoints.
            # It might be worth looking into ESTIMATED points...
            if point.get("quality") != "ACTUAL":
                continue

            interval = BCHydroInterval(
                point.get("dateTime"), point.get("endTime")
            )

            usage.append(
                BCHydroDailyElectricity(
                    type=point.get("type"),
                    quality=point.get("quality"),
                    consumption=point.get("value"),
                    interval=interval,
                    cost=point.get("cost"),
                )
            )

        rates_node = root.find("Rates")
    except Exception as e:
        raise BCHydroInvalidDataException(e)

    rates = BCHydroRates(
        rates_node.get("daysSince"),
        rates_node.get("cons2date"),
        rates_node.get("cost2date"),
        rates_node.get("estCons"),
        rates_node.get("estCost"),
    )

    return usage, rates
    # usage = BCHydroDailyUsage(
    #     electricity=new_usage, rates=rates, account=account
    # )