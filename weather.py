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
                width: 600px;
            }}
            table {{
                table-layout: fixed;
                width: 600px;
            }}
            td, th {{
                padding-top: 1em;
                white-space: pre;
                vertical-align: top;
                font-weight: normal;
            }}
        </style>
    </head>
    <body>
        <div style="white-space: pre; padding-top: 3em">Current:</div>
        <div>
            {current}
        </div>
        <div>
            {sunrise}
        </div>
        <div>
            {sunset}
        </div>
        <div>
            {data}
        </div>
        <div style="padding-top: 3em">
            Generated: {time}
        </div>
    </body>
</html>
"""
req = Request("https://wttr.in/Denver?format=j1")
res = urlopen(req)
charset = res.headers.get_content_charset()

body = res.read()
if charset:
    body = body.decode(charset)

result = json.loads(body)

current = [
    [
        get_ascii_art(result["current_condition"][0]["weatherDesc"][0]["value"]),
        f"""<span style="font-size: 40px">{result['current_condition'][0]['temp_F']} F</span>""",
    ]
]


def render_cell(hourly):
    desc = hourly["weatherDesc"][0]["value"]
    temp = f"""<span style="font-size: 28px">{hourly['tempF']} F</span>"""
    windy = ""
    if int(hourly["windspeedMiles"]) > 10:
        windy = "windy!"
    return f"{desc}\n{temp}\n{windy}"


today = result["weather"][0]
tomorrow = result["weather"][1]
dayafter = result["weather"][2]

headers = [
    "",
    f"<b>Today\n{today['date'][5:]}</b>",
    f"<b>Tomorrow\n{tomorrow['date'][5:]}</b>",
    f"<b>&nbsp;\n{dayafter['date'][5:]}</b>",
]

data = [
    headers,
    [
        "9 AM",
        render_cell(today["hourly"][3]),
        render_cell(tomorrow["hourly"][3]),
        render_cell(dayafter["hourly"][3]),
    ],
    [
        "Noon",
        render_cell(today["hourly"][4]),
        render_cell(tomorrow["hourly"][4]),
        render_cell(dayafter["hourly"][4]),
    ],
    [
        "9 PM",
        render_cell(today["hourly"][7]),
        render_cell(tomorrow["hourly"][7]),
        render_cell(dayafter["hourly"][7]),
    ],
]

generated = (
    datetime.datetime.now()
    .astimezone(pytz.timezone("America/Denver"))
    .replace(microsecond=0)
    .isoformat()
)

print(
    HTML_TEMPLATE.format(
        current=tabulate(current, tablefmt="unsafehtml"),
        sunrise=f"sunrise: {result['weather'][0]['astronomy'][0]['sunrise']}",
        sunset=f"sunset : {result['weather'][0]['astronomy'][0]['sunset']}",
        data=tabulate(data, tablefmt="unsafehtml"),
        time=generated,
    )
)
