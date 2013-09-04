## Forecast.io weather scrapers
======================

In order to add weather data to our models, we use the [Forecast.io API](https://developer.forecast.io/docs/v2). 

- `forecastio` is python wrapper to the forecast.io API that makes it easier to use. we use it in all other scripts.
- `historical_boston.py` and `historical_washingtondc.py` get historical weather data for those two cities and inserts it to a postgreSQL database. The tables we're insering this data to are created in `data/createdb.sql`. 
- `weather_updater.py` gets current forecast for DC, Boston, New York and Chicago and adds them to the database. `update_script.sh` simple executes this file; configure it to run in your crontab once an hour to continuously fetch hourly weather data. You will also need to change the path for the script. 

**Note:** You will need to set an environmental variable `FORECASTIOKEY` equal to your Forecast.io API key for these scripts to work.
