## kindle-weather

This is a repo I use to render a PNG for use with
[kindle-dash](https://github.com/pascalw/kindle-dash), the [National Oceanic
and Atmospheric Administration's
API](https://www.weather.gov/documentation/services-web-api) and
[wttr](https://wttr.in). It is [not very pretty](sample.png), but it works :)

## LICENSE

Public domain.

## running via cron

I run this via cron:

    55 * * * * /var/www/html/vhosts/tycho.pizza/dash/weather.sh /var/www/html/vhosts/tycho.pizza/dash/weather.png > /tmp/weather.log 2>&1

on the 55th minute, and have the kindle set to update on the
2nd minute of the hour. Sometimes it takes the wttr.in API a
bit to respond, and if you have a server that's doing other
things, spinning up webkit and such can take a bit to render
things as a png.
