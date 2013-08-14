# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

import os

import psycopg2
import numpy as np
import pandas as pd
import patsy
import statsmodels.api as sm

from pandas.io.parsers import read_csv

# Connect to postgres db
conn = psycopg2.connect("dbname="+os.environ.get('dbname')+" user="+os.environ.get('dbuser')
+ " host="+os.environ.get('dburl'))
cur = conn.cursor()

# <codecell>

# Fetch data for station 17 in Washington, DC - 16th & Harvard St NW, terminalName: 31103
station_id = str(17)
cur.execute("SELECT * FROM bike_ind_washingtondc WHERE tfl_id = " + station_id + ";")
station_data = cur.fetchall()

# <codecell>

# Put data in pandas dataframe
station_updates = pd.DataFrame.from_records(station_data, columns = ["station_id", "bikes_available", "spaces_available", "timestamp"], index = "timestamp")

# Convert UTC timezone of the timestamps to DC's Eastern time
station_updates.index = station_updates.index.tz_localize('UTC').tz_convert('US/Eastern')

print station_updates

# <codecell>

def find_hourly_arr_dep_deltas(station_updates):
    # Find changes (deltas) in bike count
    bikes_available = station_updates.bikes_available

    deltas = bikes_available - bikes_available.shift()

    # Show the histogram of the deltas. Need to remove outliers first.
    # clipped_deltas = deltas[(deltas > -6) & (deltas < 6)]
    # clipped_deltas.hist(bins=11)
    
    # Separate positive and negative deltas
    pos_deltas = deltas[deltas > 0]
    neg_deltas = abs(deltas[deltas < 0])

    # Count the number of positive and negative deltas per half hour per day, add them to new dataframe.
    time_interval = '1H'
    pos_interval_counts_null = pos_deltas.resample(time_interval, how ='sum')
    neg_interval_counts_null = neg_deltas.resample(time_interval, how ='sum')

    # Set NaN delta counts to 0
    # By default the resampling step puts NaN (null values) into the data when there were no observations
    # to count up during those thirty minutes. 
    arrivals = pos_interval_counts_null.fillna(0)
    departures = neg_interval_counts_null.fillna(0)

    arrival_departure_deltas = pd.DataFrame(arrivals, columns=["arrivals"])
    arrival_departure_deltas['departures'] = departures

    return arrival_departure_deltas

def remove_rebalancing_deltas(arrival_departure_deltas, rebalancing_data, station_id):

    # Define station id to terminalname mapper
    # Stations in the rebalancing trip data are identified by a 'terminalName' numerical id
    # that corresponds to the station ids in the bike update data.
    station_id_2_terminal_name = { 17 : 31103 }


    # Read in csv of rebalancing trips
    print >> sys.stderr, "Loading rebalancing data!"
    rebalancing_trips = read_csv(rebalancing_data)

    # Fetch the station's terminalname
    station_terminal_name = station_id_2_terminal_name[station_id]

    # Get rebalancing trips that start/depart and end/arrive at the station
    rebalancing_departures = rebalancing_trips[rebalancing_trips['Start terminal'] == station_terminal_name ]
    rebalancing_arrivals = rebalancing_trips[rebalancing_trips['End terminal'] == station_terminal_name ]

    # Convert departing and arriving trip times to timestamps, add datetimeindex to both.
    print >> sys.stderr, "Timestamping the data!"

    rebalancing_departures["Start date"] = pd.to_datetime(rebalancing_departures["Start date"])
    rebalancing_departures = pd.DataFrame.from_records(rebalancing_departures, index = "Start date")

    rebalancing_arrivals["End date"] = pd.to_datetime(rebalancing_arrivals["End date"])
    rebalancing_arrivals = pd.DataFrame.from_records(rebalancing_arrivals, index = "End date")

    # Count rebalancing trip arrivals and departures per hour
    print >> sys.stderr, "Getting hourly counts!"

    rebalancing_departures['Departures'] = 1
    rebalancing_arrivals['Arrivals'] = 1

    hourly_departure_counts = rebalancing_departures['Departures'].resample('1H', sum)
    hourly_arrival_counts = rebalancing_arrivals['Arrivals'].resample('1H', sum)

    # Align postive and negative deltas, our estimates of hourly arrivals and departures, with hourly counts 
    # of rebalancing arrivals and departures. The bike station data goes back further than the rebalancing
    # data, so we only want to estimate on the observations that fill within the rebalancing data timeframe
    # and that we can clean.
    print >> sys.stderr, "Getting total and rebalancing counts!"

    total_departures, rebalancing_departures = arrival_departure_deltas['departures'].align(hourly_departure_counts, join='inner')
    total_arrivals, rebalancing_arrivals = arrival_departure_deltas['arrivals'].align(hourly_arrivals_counts, join='inner')

    print >> sys.stderr, "Check to see if total and rebalancing departures aligned correctly:"
    print total_departures.head(30), rebalancing_departures.head(30)

    # Calculate rider-only arrivals and departures
    # Subtract hourly rebalancing arrivals from (estimated) hourly total arrivals to get (estimated) rider-only arrivals.

    hourly_rider_departures = total_departures - rebalancing_departures
    hourly_rider_arrivals = total_arrivals - rebalancing_arrivals

    clean_arrival_departure_deltas = (hourly_rider_arrivals, hourly_rider_departures)

    # THIS IS A TUPLE OF SERIES, BUT FIT_POISSON EXPECTS A DATAFRAME. MAKE IT WORK.
    return clean_arrival_departure_deltas

def fit_poisson(arrival_departure_deltas):
    
    # Extract months for Month feature, add to model data
    delta_months = arrival_departure_deltas.index.month
    arrival_departure_deltas['months'] = delta_months

    # Extract hours for Hour feature
    delta_hours = arrival_departure_deltas.index.hour
    arrival_departure_deltas['hours'] = delta_hours

    # Extract weekday vs. weekend variable
    delta_dayofweek = arrival_departure_deltas.index.weekday

    delta_weekday_dummy = delta_dayofweek.copy()
    delta_weekday_dummy[delta_dayofweek < 5] = 1
    delta_weekday_dummy[delta_dayofweek >= 5] = 0

    arrival_departure_deltas['weekday_dummy'] = delta_weekday_dummy

    print arrival_departure_deltas
    print arrival_departure_deltas.head(20)
    
    # Create design matrix for months, hours, and weekday vs. weekend.
    # We can't just create a "month" column to toss into our model, because it doesnt
    # understand what "June" is. Instead, we need to create a column for each month
    # and code each row according to what month it's in. Ditto for hours and weekday (=1).
    
    y_arr, X_arr = patsy.dmatrices("arrivals ~ C(months, Treatment) + C(hours, Treatment) + C(weekday_dummy, Treatment)", arrivals_departures, return_type='dataframe')
    y_dep, X_dep = patsy.dmatrices("departures ~ C(months, Treatment) + C(hours, Treatment) + C(weekday_dummy, Treatment)", arrivals_departures, return_type='dataframe')

    # Fit poisson distributions for arrivals and departures, print results
    arr_poisson_model = sm.Poisson(y_arr, X_arr)
    arr_poisson_results = arr_poisson_model.fit()
    
    dep_poisson_model = sm.Poisson(y_dep, X_dep)
    dep_poisson_results = dep_poisson_model.fit()
    
    print arr_poisson_results.summary(), dep_poisson_results.summary()
    
    poisson_results = [arr_poisson_results, dep_poisson_results]
    
    return poisson_results

# <codecell>

# Predict *net* lambda value some time in the future, using the list of hours created above.
# You can predict any number of hours ahead using interval_length, default is set to 1 hour.

# The arrival lambda at 12pm actually means the expected arrival rate from 12pm to 1pm. But if the
# current time is 12:15pm and you're estimating an hour ahead to 1:15pm, you need to find
# 3/4ths of the lambda from 12pm - 1pm and add it to 1/4th of the lambda from 1pm to 2pm.
# This section returns the total lambda over that interval, during which the rate is changing.

# It also works for predictions multiple hours ahead, as all those lambdas will be summed
# and yield a large expected value, which makes sense if you're counting bikes over several hours.

# The function predicts arrival lambdas across the time interval, does the same thing independently
# for departure lambdas, and finds their difference to get the net lambda at that time - the change in bikes
# you'll see at the station in an hour. Add the net lambda to the current number of bikes to get
# the prediction of the expected value of how many bikes will be there.

def predict_net_lambda(current_time, prediction_interval, month, weekday, poisson_results):
    "Compute the net lambda value - change in bikes at station - for a specific time interval (hour), month, and weekday."
    
    # Define function that takes in a month, time, weekday and returns 
    # a lambda - the expected value of arrivals or departures during that hour (given that month)
    # - using the covariate coefficients estimated above.
    def lambda_calc(month, time, weekday, poisson_results):
        "Compute the lambda value for a specific month, time (hour), and weekday."
        
        # Pull out coefficient estimates for the factored covariants
        estimates = poisson_results.params
    
        # Fetch intercept
        intercept = estimates['Intercept']
        
        # Fetch coefficient estimate that corresponds to the month..
        if month == 1:
            month_estimate = 0
        else:
            month_estimate = estimates['C(months, Treatment)[T.'+str(month)+']']
    
        # .. to the hour
        hour = floor(time)
        if hour == 1:
            hour_estimate = 0
        else:
            hour_estimate = estimates['C(hours, Treatment)[T.'+str(int(hour))+']']
    
        # .. and to the weekday status.
        if weekday == 0:
            weekday_estimate = 0
        else:
            weekday_estimate = estimates['C(weekday_dummy, Treatment)[T.'+str(weekday)+']']
    
        # Compute log lambda, which is linear function of the hour, month, and weekday coefficient estimates
        log_lambda = intercept + month_estimate + hour_estimate + weekday_estimate
        
        # Raise e to the computed log lambda to find the estimated value of the Poisson distribution for these covariates.
        est_lambda = exp(log_lambda)
        
        return est_lambda
    
    # Create list of hours in between the current time and the prediction time
    # Need to do this to calculate cumulative rate of arrivals and departures
    prediction_time = current_time + prediction_interval

    time_list = [current_time]
    next_step = current_time
    while next_step != prediction_time:
    
        if floor(next_step) + 1 < prediction_time:
            next_step = floor(next_step) + 1
            time_list.append(next_step)
        
        else:
            next_step = prediction_time
            time_list.append(next_step)
        
    
    # Calculate the cumulative lambda rate over the predition interval
    arr_cum_lambda = 0 
    dep_cum_lambda = 0 
    
    # Find cumulative lambda for arrivals..
    for i in range(1, len(time_list)):
        est_lambda = lambda_calc(month, time_list[ i - 1 ], weekday, poisson_results[0])
        hour_proportion = time_list[i] - time_list[ i - 1 ]
    
        interval_lambda = est_lambda * hour_proportion
        
        arr_cum_lambda += interval_lambda
        
    # .. and departures
    for i in range(1, len(time_list)):
        est_lambda = lambda_calc(month, time_list[ i - 1 ], weekday, poisson_results[1])
        hour_proportion = time_list[i] - time_list[ i - 1 ]
    
        interval_lambda = est_lambda * hour_proportion
        
        dep_cum_lambda += interval_lambda
    
    net_lambda = arr_cum_lambda - dep_cum_lambda
    
    return net_lambda

#<codecell>

# Convert bike availability time series into hourly interval count data
arrival_departure_deltas = find_hourly_arr_dep_deltas(station_updates)

# Remove hourly swings in bike arrivals and departures caused by station rebalancing
rebalancing_data = '../data/rebalancing_trips_2_2012_to_3_2013_sample.csv'

# THIS IS A TUPLE OF SERIES, BUT FIT_POISSON EXPECTS A DATAFRAME. MAKE IT WORK. need to check that both series have same length/timeframe
# and can live in a dataframe.
clean_arrival_departure_deltas = remove_rebalancing_deltas(arrival_departure_deltas, rebalancing_data, station_id)

# Estimate the poisson point process
poisson_results = fit_poisson(clean_arrival_departure_deltas)

# Try to predict!
current_time = 17.5
prediction_interval = 1
month = 5
weekday = 0

bike_change = predict_net_lambda(current_time, prediction_interval, month, weekday, poisson_results)
print "The change in bikes at time %s and month %s is %s" % (str(floor(current_time)), str(month), str(bike_change))

# Plot predictions of available bikes by hour for given covariates
init_bikes = 22
bike = init_bikes
bikes = [init_bikes]
hours_of_day  = range(1,24)

for hour in hours_of_day:
    bike += predict_net_lambda(hour, prediction_interval, month, weekday, poisson_results)
    bikes.append(bike)
       
pd.Series(bikes).plot()


# <codecell>

# Validate the model!
# min_time_pt = datetime.datetime(2010,10,8)
# prediction_interval =
# time_step =


# def validate_model(min_time_pt):
    
    # Generate list of time points incremented by the time_step
    
    # Get observations before timepoint
    # smaller_updates = station_updates[:min_time_pt]
    
    # print station_updates
    # print smaller_updates

# validate_model(min_time_pt)

# <codecell>

# Simulate bike availability at station 17 for next half hour

# We're doing this to flag when station is full or empty, which
# is what bikeshare operators want.

# <codecell>


