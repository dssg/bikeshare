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

## Data

The data is based off of BIXI Data, in minute by minute snapshots.

**There are two BIXI systems, BIXIV1 (Boston, Washington DC & Minneapolis) and BIXIV2 (Chicago and New York City)**

###Schema, BIXIV1

* Indiv
	* tfl_id 
	* bikes
	* spaces      
	* timestamp   
* Agg 
	* timestamp     
	* bikes
	* spaces
	* unbalanced 

###Schema, BIXIV2
* Indiv
	* tfl_id   
	* bikes
	* spaces 
	* total_docks 
	* timestamp
* Agg
 	* timestamp    
	* bikes
	* spaces 
	* unbalanced
	* total_docks 

### Scrapers
Scrapers are built to get the metadata for the database. Many thanks to Anna Meredith & [Patrick Collins](https://github.com/capitalsigma) for their code contributions on this. 

### Notes	
The difference in ordering is a known, legacy issue. 

Total docks _(V2 Only)_ = unavailable docks (presumed bike marked as broken or dock itself broken) + bikes + spaces.


While we are on the topic, note that the timestamp I report is my own timestamp rather than an operator-supplied timestamp. The two should normally agree to within a couple of minutes, except if the operator is having system issue which causes the feed to still be available but not update.

I also don't currently record dock statuses (e.g. temporary, active, locked, bonus), locations, names, addresses, or other available metadata.

## Contributing
To get involved, please check the [issue tracker](issues).

To get in touch, email Hunter Owens at owens.hunter@gmail.com.


