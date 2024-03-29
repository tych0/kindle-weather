import datetime
import json
import subprocess
import re
from urllib.request import Request, urlopen

from tabulate import tabulate

import pytz

HTML_TEMPLATE = """
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN"
"http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">

<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">
    <head>
        <meta http-equiv="Content-Type" content="text/html;charset=utf-8"/>
        <title>Weather</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
        <style>
            body {{
                font-family: monospace;
                font-size: 20px;
                justify-content: center;
            }}
            div {{
                display: block;
            }}
            table {{
                width: 580px;
            }}
            td, th {{
                padding-top: 1em;
                padding-right: 1em;
                vertical-align: top;
                font-weight: normal;
            }}
            .current-weather {{
                font-size: 40px;
            }}
        </style>
    </head>
    <body>
        <div class="current-weather">
            {current}
        </div>
        <div>
            {sunrise} {sunset}
        </div>
        <div>
            {data}
        </div>
        <div style="width: 580px">
            {detailed}
        </div>
        <div style="padding-top: 1em">
            Generated: {time}
        </div>
    </body>
</html>
"""

def make_req(url):
    req = Request(url)

    req.add_header(
        "User-Agent", "(https://github.com/tych0/kindle-weather, tycho@tycho.pizza)"
    )
    res = urlopen(req)
    charset = res.headers.get_content_charset()

    body = res.read()
    if charset:
        body = body.decode(charset)
    result = json.loads(body)
    return result

# https://www.weather.gov/documentation/services-web-api
# points found by https://api.weather.gov/gridpoints/39.7490,-105.0484 (middle of sloan's lake)
hourly_forecast = make_req("https://api.weather.gov/gridpoints/BOU/60,61/forecast/hourly")

wttr_result = make_req("https://wttr.in/Denver?format=j1")
sunrise=f"sunrise: {wttr_result['weather'][0]['astronomy'][0]['sunrise']}"
sunset=f"sunset: {wttr_result['weather'][0]['astronomy'][0]['sunset']}"

current = [
    [
        hourly_forecast["properties"]["periods"][0]["shortForecast"],
        hourly_forecast['properties']['periods'][0]['temperature'],
    ]
]


MT = pytz.timezone("America/Denver")

today = datetime.datetime.now().astimezone(MT).date()
tomorrow = today + datetime.timedelta(days=1)
dayafter = tomorrow + datetime.timedelta(days=1)

headers = [
    "",
    f"<b><div>Today</div><div>{today.strftime('%m-%d')}</div></b>",
    f"<b><div>Tomorrow</div><div>{tomorrow.strftime('%m-%d')}</div></b>",
    f"<b><div>&nbsp;</div><div>{dayafter.strftime('%m-%d')}</div></b>",
]

offset = datetime.datetime.now().astimezone(MT).hour + 1
periods = hourly_forecast["properties"]["periods"]


def render_cell(offset):
    if offset < 0:
        return "N/A"
    hourly = periods[offset]
    desc = hourly["shortForecast"]
    temp = f"""<span style="font-size: 28px">{hourly['temperature']} F</span>"""
    windy = ""
    if int(hourly["windSpeed"].split(" ")[0]) > 10:
        windy = "windy!"
    return f"<div>{desc}</div><div>{temp}</div><div>{windy}</div>"


times = [
    ("9 AM", 9),
    ("Noon", 12),
    ("2 PM", 14),
    ("9 PM", 21),
]

data = [
    [
        header,
        render_cell(t - offset),
        render_cell(24 + t - offset),
        render_cell(24 + 24 + t - offset),
    ]
    for (header, t) in times
]

generated = (
    datetime.datetime.now().astimezone(MT).replace(microsecond=0).isoformat()
)

detailed = make_req('https://api.weather.gov/gridpoints/BOU/60,61/forecast')

print(
    HTML_TEMPLATE.format(
        current=tabulate(current, tablefmt="unsafehtml"),
        data=tabulate(data, tablefmt="unsafehtml"),
        sunrise=sunrise,
        sunset=sunset,
        detailed=detailed["properties"]["periods"][0]["detailedForecast"],
        time=generated,
    )
)
