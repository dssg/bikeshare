This is a [Data Science for Social Good](http://www.dssg.io) data science project to predict when bikeshare stations will be empty or full in major American cities.

## The problem: bikeshare rebalancing

The City of Chicago just launched Divvy, a new bike share system designed to connect people to transit, and to make short one-way trips across town easy. Bike share is citywide bike rental - you can take a bike out at a station on one street corner and drop it off at another.

![Divvy bike share](http://dssg.io/img/partners/divvy.jpg)

Popular in Europe and Asia, bike share has landed in the United States: Boston, DC, and New York launched systems in the past few years, San Francisco and Seattle are next.

These systems share a central flaw, however: because of commuting patterns, bikes tend to pile up downtown in morning and on the outskirts in the afternoon. This imbalance can make using bikeshare difficult, because people can’t take out bikes from empty stations, or finish their rides at full stations.

To prevent this problem, bikeshare operators drive trucks around to reallocate bikes from full stations to empty ones. In bikeshare parlance, this is called **rebalancing**.

Right now, operators do rebalancing by [looking at how long](http://www.cabitracker.com/status.php) stations have been empty or full and dispatching the nearest available rebalancing truck. So they can only see the **current number of bikes** at each station - not how many will be there in an hour or two.

![Chicago Department of Transportation](http://dssg.io/img/partners/cdot.jpg)

We’re working with the City of Chicago’s [Department of Transportation](http://www.cityofchicago.org/city/en/depts/cdot.html) to change this: by analyzing weather and bikeshare station trends, we’ll predict how many bikes are likely to be at each Divvy station in the future.

There's a catch, however: to predict things in the future, you need lots of data about the past. And since Divvy just launched, there's not much data about Chicago bikeshare yet. 

But it turns out that [Alta Bike Share](http://www.altabicycleshare.com/), the company operating Divvy, also runs the older bikeshare systems of Boston and DC, for which we have several years of station data. So we're creating predictive statistical models for those cities first, and we'll apply them to Chicago once there's enough data. 

## The solution: time series regression
To predict the number of bikes at bike share stations in DC and Boston, we're going to use time series statistical techniques. Specifically, we're going to try to predict how many bikes will be at every station in each city's bikeshare system 60 minutes from now.

To make this prediction, we're using a [Auto Regressive Moving Average (ARMA)](http://en.wikipedia.org/wiki/Autoregressive%E2%80%93moving-average_model) regression model. This model will take in the current number of bikes at a station, the current time, day of week, month, and eventually weather conditions, and spit out the estimated number of bikes that will be at that station in 60 minutes.


## The project
There are three components to the project:

**A database storing historical bikeshare and weather data**

Thanks to [Oliver O'Brien](http://oliverobrien.co.uk/bikesharemap/), we've got historical data on the number of bikes and docks available at every bikeshare station in DC and Boston since their systems launched. We're storing this data in postgreSQL database, and updating it constantly by hitting Atla's real-time bikeshare APIs. The data is discussed in further detail below.

Scripts to build the database, load historical data into it, and add real-time data to it are in the `data` and `scrapers` folders. The database updates every minute using a cron job that you need schedule on your own machine.

**A model that uses this data to predict future number of bikes**

The model lives in `model`. There are scripts in there that crunch the historical data in the database to estimate the model's parameters, and other that actually implement the model by consuming these parameters, fetching model inputs from the database, and spitting out predictions.

*This directory is undergoing heavy development*

**A simple webapp that displays the model's predictions**

The app, which uses flask and bootstrap, lives in `web`. We use [MapBox.js](http://mapboxjs.org) for mapping. Simply run `python app.py` to deploy the application on localhost. 

To install either needed python dependencies, clone the project and run `pip install -r requirements.txt`

## The data: real-time bikeshare station availability and weather

Alta bikeshare runs the bikeshare systems in [Boston](thehubway.com/), [Washington DC](http://www.capitalbikeshare.com/), [Minneapolis](https://www.niceridemn.org/), [New York](http://citibikenyc.com/) and [Chicago](http://divvybikes.com/). Each system exposes either an XML ("Version 1") or JSON ("Version 2") API. 

Every few minutes, these APIs provide the location of each station, and the number of avaliable bikes and free spaces at the station.  

An example of Alta's XML API is [Boston](http://www.thehubway.com/data/stations/bikeStations.xml). [Chicago](http://divvybikes.com/stations/json) uses the JSON API. Each version of the API has a different data schema, explained below.

Researcher Oliver O'Brien has been crawling these APIs since each system launched, getting data from them every 2 minutes. He gave us this historical data, which we imported into a PostgreSQL database. To add to this historical data, we've written scrapers (`scrapers`) that update our database every minute. Unfortunately, we can't open O'Brien's historical data at this time, but you're welcome to use our scrapers to gather your own data.

We also use historical weather data to aid our predictive model. We've written scripts to get it from Forecast.io (details below).

### Schema of XML API (Version 1)
* XML API cities are Boston, Washington DC and Minneapolis. They use the following schema:

* Indiv (The Tablenames are `bike_ind_cityname`, ie `bike_ind_boston`)

|tfl_id | bikes | spaces |timestamp|
|------|:-----:|:-------:|:-----------------------|
| 5	| 7 | 10	| 2011-07-28 11:58:12 |
| 8 	| 5 | 6 	| 2011-07-28 11:58:12 |

* Agg (The Tablename are `bike_agg_cityname`, ie `bike_agg_boston`)

timestamp | bikes | spaces | unbalanced 
---------------------|:----:|:------:|:----
2013-07-04 17:54:03| 838 | 1058 | 364
2013-07-04 17:52:03| 826 | 1070 | 368

###Schema, BIXIV2
* JSON API cities are Chicago and New York. They use a slightly different schema:

* Indiv

tfl_id | bikes | spaces | total_docks | timestamp
---------|:---------:|:--------:|:---------:|:----------
  72 | 0 | 39 | 39 | 2013-05-24 19:32:02  
  79 | 15 | 15 | 32 | 2013-05-24 19:32:02  

* Agg

timestamp | bikes | spaces | unbalanced |total_docks 
-----------------|:---------:|:--------:|:---------:|:----------
2013-07-04 17:58:04 |  3670 |   6900 |       2007 |       11285 
2013-07-04 17:56:04 |  3677 |   6893 |       2017 |       11285   

### Notes on our PostgreSQL configuration
We maintain cityname naming conventions: (These are way city names are represented in the database) of 
`newyork`,`washingtondc`,`boston`,`minneapolis`,`chicago`

A series of metadata tables also exist in our PostgreSQL to tie a station's id (the `tfl_id` field) to its lat/long and other info. The tablenames follow the `metadata_cityname` convention, i.e. `metadata_boston`.

### Scrapers
We've built scrapers to fetch real-time bike station and weather data.

- Database update scrapers are used within a cronjob to keep updated the `ind` tables each minute. You need to set up this cronjob yourself if duplicating the database. 

- Metadata scrapers are for the metadata tables. Many thanks to Anna Meredith & [Patrick Collins](https://github.com/capitalsigma) for their code contributions on this. 

- Weather scraper get data from [Forecast.io](http://forecast.io), using the corresponding [python wrapper](https://github.com/ZeevG/python-forcast.io). To keep/get the weather data you'll need a forecast.io API key. Follow the below steps to retrieve the weather data. 
	1.  Set the `dbuser`,`dbname`,and `dburl` environmental varibles to the proper credentials for postgres. Also set the `FORECASTIOKEY` environmental variable to your forecast.io key. 
	2. Make sure that the tables specified in `data/create_db.sql` exist.
	3. Each city has its own script to load weather data, named as `historical_[[city_name]].py`. Simply run that script to load in the data for each city. 

## Contributing to the project
To get involved, please check the [issue tracker](https://github.com/dssg/bikeshare/issues).

To get in touch, email Hunter Owens at owens.hunter@gmail.com.
