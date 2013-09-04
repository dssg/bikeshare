## Weather Scrapers ##
======================

In order to add weather data to our models, we use the [Forecast.io API](http://forecast.io). Configure `update_script.sh` in your crontab to run once an hour. You will also need to change the path for the script. 

*You will need to set an environmental varible `FORECASTIOKEY` equal to your Forecast.io API key in order for the scripts to work.*

The scrapers are either to get historical data and/or update it. The tables are created in `data/createdb.sql`. 