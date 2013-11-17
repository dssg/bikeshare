# Predictive bikeshare rebalancing

<a href="http://divvybikes.com/"><img src="http://dssg.io/img/partners/divvy.jpg" align="left"></a>
<a href="http://www.cityofchicago.org/city/en/depts/cdot.html"><img src="http://dssg.io/img/partners/cdot.jpg" align="left"></a>


Statistical models and app for predicting when bikeshare stations will be empty or full in Washington DC and someday Chicago.  **The app is live at [bikeshare.dssg.io](http://bikeshare.dssg.io).**

This project is a part of the 2013 [Data Science for Social Good](http://www.dssg.io) fellowship, in partnership with [Divvy](http://divvybikes.com/) and the [Chicago Department of Transportation](www.cityofchicago.org/city/en/depts/cdot.html).

*For a quick and gentle overview of the project, check out our [blog post](http://dssg.io/2013/08/09/divvy-helping-chicagos-new-bike-share.html).*

## The problem: bikeshare rebalancing

The City of Chicago just launched [Divvy](http://divvybikes.com/), a new bike sharing system designed to connect people to transit, and to make short one-way trips across town easy. [Bike sharing](http://en.wikipedia.org/wiki/Bicycle_sharing_system) is citywide bike rental - you can take a bike out at a station on one street corner and drop it off at another.

Bike sharing systems share a central flaw: because of commuting patterns, bikes tend to pile up downtown in morning and on the outskirts in the afternoon. This imbalance can make using bikeshare difficult, because people can’t take out bikes from empty stations, or finish their rides at full stations.

To prevent this problem, bikeshare operators drive trucks around to reallocate bikes from full stations to empty ones. In bikeshare parlance, this is called **rebalancing**.

Right now, they do this by looking at the **current number of bikes** at each station - not how many will be there in an hour or two.

We’re working with the City of Chicago’s [Department of Transportation](http://www.cityofchicago.org/city/en/depts/cdot.html) to make bikeshare rebalancing more proactive: by analyzing weather and bikeshare station trends, we can **predict how many bikes** are likely to be at each Divvy station in the future.

However, since there's not much bike sharing data for Chicago yet, we're first developing predictive models for Capital Bikeshare, Washington DC's bike sharing system.

**[Read more about bikeshare rebalancing on our blog](http://dssg.io/2013/08/09/divvy-helping-chicagos-new-bike-share.html)**

## The solution: Poisson regression
To predict the number of bikes at bike share stations in DC, we're using [Poisson regression](http://www.umass.edu/wsp/statistics/lessons/poisson/), a statistical technique useful for modeling counts. 

Specifically, we take the current time of day, day of week, month, and weather as inputs into our model, and try to predict the number of bike arrivals and departures we expect to see at a given bike share station over the next 60 minutes. We subtract departures from arrivals to find the net change in bikes over the hour, and add this change to the current number of bikes to get our predicted bikes at the station in 60 minutes. 

<a href="http://bikeshare.dssg.io"><img src="https://raw.github.com/dssg/bikeshare/master/for_wiki/webapp_screenshot.png" align="center"></a>

We do this for every station in DC's bikeshare system, and display the resulting predictions in a [human-friendly web app](http://bikeshare.dssg.io).

**[Read more about our statistical model in the wiki](../../wiki/methodology)**

## The data: real-time bikeshare station availability and weather

[Alta bikeshare](http://www.altabicycleshare.com/) - the company that runs the bikeshare systems in [Boston](http://www.thehubway.com/), [Washington DC](http://www.capitalbikeshare.com/), [New York](http://citibikenyc.com/), [Chicago](http://divvybikes.com/), and others - publishes real-time bike availability data for these cities through an API.

Every minute or two, the API reports the number of bikes and docks available at each bikeshare station in the city's system:

```json
{
	"id":17,
	"stationName": "Wood St & Division St",
	"location": "1802 W. Divison St",
	"availableBikes": 6,
	"availableDocks": 9,
	"totalDocks": 15,
	"latitude": 41.90332,
	"longitude": -87.67273,		
	"statusValue": "In Service",
}
```

We're using historical bike availability data for DC - courtesy of urban researcher [Oliver O'Brien](http://www.oliverobrien.co.uk) - and historical weather data from [Forecast.io](http://www.forecast.io) to fit our Poisson model.

To make predictions, we get real-time bike availability and weather data from Alta's DC API and Procure.io, and plug these inputs into our model. 

**[Read more about how we're getting data in the wiki](../../wiki/data)**

## Project layout
There are three components to the project:

### **A database storing historical bikeshare and weather data**

Thanks to [Oliver O'Brien](http://oliverobrien.co.uk/bikesharemap/), we've got historical data on the number of bikes and docks available at every bikeshare station in DC and Boston since their systems launched. We're storing this data in postgreSQL database, and updating it constantly by hitting Atla's real-time bikeshare APIs. [Read our wiki](../../wiki/data) for more detail on these data sources.

Scripts to build the database, load historical data into it, and add real-time data to it are in the `data` and `scrapers` folders. The database updates every minute using a cron job that you need schedule on your own machine.

### **A model that uses this data to predict future number of bikes**

The Poisson model lives in `model`. There's also a binomial logistic model we implemented in there. Exploratory data analysis that informed the model choice lives in `analysis`.

There are scripts in `model/possion` that crunch the historical data in the database to estimate the model's parameters, and others that use the model to predict by consuming these parameters, fetching real-time model inputs from the database, and spitting out predictions. We also have model validation scripts that measure our model's predictive accuracy.

### **A simple webapp that displays the model's predictions**

The webapp is currently live at [bikeshare.dssg.io](http://bikeshare.dssg.io/).

The app, which uses flask and bootstrap, lives in `web`. We use [MapBox.js](http://www.mapbox.com/mapbox.js/api/v1.3.1/) for mapping. Simply run `python app.py` to deploy the application on localhost. 

To install either needed python dependencies, clone the project and run `pip install -r requirements.txt`

## Installation 

To get the project running locally, first to clone the repo:
````
git clone https://github.com/dssg/bikeshare
cd bikeshare/
````

### Database Configuration 
You will need a working [PostgreSQL](http://www.postgresql.org) 9.x series install. Once you have that, run `data/create_db.sql` to create all the appropriate tables. 

### Scraper Configuration 
We use several scrapers to populate the data in the database. Inside `scrapers` there is more detailed install instructions and example crontabs. You will need a [forecast.io](http://forecast.io/developer) API key. Historical data will be made avalible shortly. 

### Webapp Installation

To the run the flash web app, you'll need to create a new python [virtual environment](http://docs.python-guide.org/en/latest/dev/virtualenvs/), install needed python modules using [pip](http://dubroy.com/blog/so-you-want-to-install-a-python-package/), and run the flask server:

```bash
cd bikeshare/web
virtualenv ./
. bin/activate
pip install -r requirements.text
python web/app.py
```

To deploy the webapp in a production environment, use [Gunicorn](http://gunicorn.org/) & [nginx](http://nginx.org/) web servers.


## Contributing to the project
To get involved, please check the [issue tracker](https://github.com/dssg/bikeshare/issues).

To get in touch, email the team at BlueSteal@googlegroups.com.

## License 

Copyright (C) 2013 [Data Science for Social Good Fellowship at the University of Chicago](http://dssg.io)

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
