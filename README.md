# Bikeshare Prediction Project

## The Problem
Bikeshare stations often become full or empty with bikes. This is bad because as a user I can't remove a bike or dock it. Bikeshare operators have trucks that drive around an move bikes from full stations to empty stations. This is called rebalancing.

Right now, they do this by [looking at how long](http://www.cabitracker.com/status.php) stations have been empty or full and dispatching the nearest rebalancing truck.

City governments and bikeshare operators want to be able to predict when stations are likely to become empty or full so they can respond proactively. 

## The Solution
We're going to use time series statistical techniques to help them do that. Specifically, we're going to try to predict how many bikes will be at every station in Washington DC's bikeshare system 60 minutes from now.

To make this prediction, we're using a [Auto Regressive Moving Average (ARMA)](http://en.wikipedia.org/wiki/Autoregressive%E2%80%93moving-average_model) regression model. This model will take in the current number of bikes at a station, the current time, day of week, month, and eventually weather conditions, and spit out the estimated number of bikes that will be at that station in 60 minutes.

There are three components to the project:

- A database storing historical data

Thanks to [Oliver O'Brien](http://oliverobrien.co.uk/bikesharemap/), we've got historical data on the number of bikes and docks available at every station in DC's bikeshare system since late 2010. We're storing this data in postgres database, and updating it by hitting DC's real-time bikeshare API. The data is discussed in the Data section below.

The scripts to build the database and add current data to it are in `scrapers` and `database` folders. The database updates every minute using a cron job.

- A model that uses this data to predict future number of bikes 

The model lives in `model`. `parameter_estimate.py` crunches the historical data in the database to estimate the model's parameters. `prediction_model.py` actually implements the model consuming these parameters and fetching near real-time station availability from the database.

- A simple webapp that displays the model's predictions 

The app, which uses flask and bootstrap, lives in `web`.

The frontend of the webapp uses [require.js](requirejs.org) to manage dependencies. 

To install either needed python depenecies, simpily clone the project and `pip install -r requirements.txt`

## Data

The data is based off of BIXI Data, in minute by minute snapshots. However, the data before 7/4/2013 is in 2 minute intervals, while the data after is in one minute intervals. 

**There are two BIXI systems, BIXIV1 (Boston, Washington DC & Minneapolis) and BIXIV2 (Chicago and New York City)**

Cityname naming conventions: (These are way city names are represented in the database) 
`newyork`,`washingtondc`,`boston`,`minneapolis`,`chicago`

###Schema, BIXIV1

* Indiv (The Tablenames are `bike_ind_cityname`, ie `bike_ind_boston`)

|tfl_id | bikes | spaces |timestamp|
|------|:-----:|:-------:|:-----------------------|
| 5	| 7 | 10	| 2011-07-28 11:58:12 |
| 8 	| 5 | 6 	| 2011-07-28 11:58:12 |

* Agg (The Tablename are `bike_agg_cityname`, ie `bike_agg_boston`)

timestamp | bikes | spaces | unbalanced 
-------------------------------|:----:|:------:|:----------
| 2013-07-04 17:54:03| 838 | 1058 | 364
| 2013-07-04 17:52:03|826 |1070 |368

###Schema, BIXIV2
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

### Metadata
A series of metadata tables exist to corrolate `tfl_id` to lat/long and other info, the tablenames are `metadata_cityname`, ie `metadata_boston`.

### Scrapers
Scrapers are built to get the metadata for the database. Many thanks to Anna Meredith & [Patrick Collins](https://github.com/capitalsigma) for their code contributions on this. 

The Weather Scrapers use [Forecast.io](http://forecast.io). They also use the corresponding [python wrapper](https://github.com/ZeevG/python-forcast.io). To keep the weather data up to date, you'll need a forecast.io API key. To prevent a unicode error when writing to csv, we use Unicode.csv. See the `requirements.txt` file.

### Notes	
The difference in ordering is a known, legacy issue. 

Total docks _(V2 Only)_ = unavailable docks (presumed bike marked as broken or dock itself broken) + bikes + spaces.


While we are on the topic, note that the timestamp I report is my own timestamp rather than an operator-supplied timestamp. The two should normally agree to within a couple of minutes, except if the operator is having system issue which causes the feed to still be available but not update.

I also don't currently record dock statuses (e.g. temporary, active, locked, bonus), locations, names, addresses, or other available metadata.

## Contributing
To get involved, please check the [issue tracker](https://github.com/dssg/bikeshare/issues).

To get in touch, email Hunter Owens at owens.hunter@gmail.com.


