This directory contains scrapers for each of the APIs we use to get data. 

- `V1` contains scripts that fetch real-time bike availability data from cities that use Alta's version 1 XML API (Boston, Washington DC, Minneapolis)

- `V2` contains scripts that fetch real-time bike availability data from cities that use Alta's version 2 JSON API (Chicago and New York)

- `Weather` contains scripts that fetch real-time and historical weather data from forecast.io

- `crontab.example` is an example version of the crontab we use to run these scrapers continously and keep our database up to date.

More info can be found in the [data section of the wiki](https://github.com/dssg/bikeshare/wiki/data).
