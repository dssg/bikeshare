# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

import os
import sys

import psycopg2
import numpy as np
import pandas as pd
import patsy
import statsmodels.api as sm

from pandas.io.parsers import read_csv
from math import floor, exp

# Connect to postgres db
conn = psycopg2.connect("dbname="+os.environ.get('dbname')+" user="+os.environ.get('dbuser')
+ " host="+os.environ.get('dburl'))
cur = conn.cursor()

# <codecell>

print >> sys.stderr, "Getting station data from postgres!"
# Fetch data for station 17 in Washington, DC - 16th & Harvard St NW, terminalName: 31103
station_id = 17
cur.execute("SELECT * FROM bike_ind_washingtondc WHERE tfl_id = " + str(station_id) + ";")
station_data = cur.fetchall()

# <codecell>

# Put data in pandas dataframe
station_updates = pd.DataFrame.from_records(station_data, columns = ["station_id", "bikes_available", "spaces_available", "timestamp"], index = "timestamp")

# Convert UTC timezone of the timestamps to DC's Eastern time
station_updates.index = station_updates.index.tz_localize('UTC').tz_convert('US/Eastern')

print >> sys.stderr, "Here's the interval data for station %s" % station_id
print >> sys.stderr, station_updates.head()

# <codecell>

def find_hourly_arr_dep_deltas(station_updates):
    print >> sys.stderr, "Computing total arrival and departure deltas for the station."
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
    
    print >> sys.stderr, "Station %s arrival and departures deltas:" % station_id
    print >> sys.stderr, arrival_departure_deltas.head()

    return arrival_departure_deltas

def remove_rebalancing_deltas(arrival_departure_deltas, rebalancing_data, station_id):

    # Define station id to terminalname mapper
    # Stations in the rebalancing trip data are identified by a 'terminalName' numerical id
    # that corresponds to the station ids in the bike update data.
    station_id_2_terminal_name = { 17 : 31103 }

    # Read in csv of rebalancing trips
    print >> sys.stderr, "Loading system-wide rebalancing trip data."
    rebalancing_trips = read_csv(rebalancing_data)

    # Fetch the station's terminalname
    station_terminal_name = station_id_2_terminal_name[station_id]

    # Get rebalancing trips that start/depart and end/arrive at the station
    rebalancing_departures = rebalancing_trips[rebalancing_trips['Start terminal'] == station_terminal_name ]
    rebalancing_arrivals = rebalancing_trips[rebalancing_trips['End terminal'] == station_terminal_name ]

    # Convert departing and arriving trip times to timezone-aware timestamps, add datetimeindex to both.
    rebalancing_departures["Start date"] = pd.to_datetime(rebalancing_departures["Start date"])
    rebalancing_departures = pd.DataFrame.from_records(rebalancing_departures, index = "Start date")
    rebalancing_departures.index = rebalancing_departures.index.tz_localize('US/Eastern')

    rebalancing_arrivals["End date"] = pd.to_datetime(rebalancing_arrivals["End date"])
    rebalancing_arrivals = pd.DataFrame.from_records(rebalancing_arrivals, index = "End date")
    rebalancing_arrivals.index = rebalancing_arrivals.index.tz_localize('US/Eastern')

    # Count rebalancing trip arrivals and departures per hour
    print >> sys.stderr, "Computing hourly rebalancing arrival and departure deltas."

    rebalancing_departures['Departures'] = 1
    rebalancing_arrivals['Arrivals'] = 1

    hourly_departure_counts = rebalancing_departures['Departures'].resample('1H', sum)
    hourly_arrival_counts = rebalancing_arrivals['Arrivals'].resample('1H', sum)

    # Make rebalancing count vectors same length.
    # Rebalancing arrival trips may start later than departures, so we need to make
    # the two rebalancing vectors the length of the longest one, otherwise we'll
    # produce NaN values on one column or the other when we put rider deltas back into a dataframe, 
    # which breaks the 
    rebalancing_deltas = pd.DataFrame(hourly_arrival_counts, columns=["arrivals"])
    rebalancing_deltas['departures'] = hourly_departure_counts
    rebalancing_deltas = rebalancing_deltas.fillna(0)

    # Align postive and negative deltas, our estimates of hourly arrivals and departures, with hourly counts 
    # of rebalancing arrivals and departures. The bike station data goes back further than the rebalancing
    # data, so we only want to estimate on the observations that fill within the rebalancing data timeframe
    # and that we can clean.
    total_departures, rebalancing_departures = arrival_departure_deltas['departures'].align(rebalancing_deltas.departures, join='inner')
    total_arrivals, rebalancing_arrivals = arrival_departure_deltas['arrivals'].align(rebalancing_deltas.arrivals, join='inner')

    print >> sys.stderr, "Check to see if total and rebalancing departure deltas correctly:"
    print >> sys.stderr, total_departures.head(20) 
    print >> sys.stderr, rebalancing_departures.head(20)

    # Calculate rider-only arrivals and departures
    # Subtract hourly rebalancing arrivals from (estimated) hourly total arrivals to get (estimated) rider-only arrivals.
    print >> sys.stderr, "Subtracting rebalancing deltas from total to get rider deltas."
    hourly_rider_departures = total_departures - rebalancing_departures
    hourly_rider_arrivals = total_arrivals - rebalancing_arrivals

    # Set negative departure or arrivals equal to 0.
    # Because our total arrival and departure deltas are estimated from 2-min interval data
    # and not true aggregated trips, you might end up with negative rider deltas, which
    # chockes our poisson estimation function.
    hourly_rider_departures[hourly_rider_departures < 0] = 0
    hourly_rider_arrivals[hourly_rider_arrivals < 0] = 0

    # Packaging rider deltas for poisson estimator
    clean_arrival_departure_deltas = pd.DataFrame(hourly_rider_arrivals, columns=["arrivals"])
    clean_arrival_departure_deltas['departures'] = hourly_rider_departures
   
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
    
    # Create design matrix for months, hours, and weekday vs. weekend.
    # We can't just create a "month" column to toss into our model, because it doesnt
    # understand what "June" is. Instead, we need to create a column for each month
    # and code each row according to what month it's in. Ditto for hours and weekday (=1).
    
    y_arr, X_arr = patsy.dmatrices("arrivals ~ C(months, Treatment) + C(hours, Treatment) + C(weekday_dummy, Treatment)", arrival_departure_deltas, return_type='dataframe')
    y_dep, X_dep = patsy.dmatrices("departures ~ C(months, Treatment) + C(hours, Treatment) + C(weekday_dummy, Treatment)", arrival_departure_deltas, return_type='dataframe')

    print >> sys.stderr, "Here's the design matrix of departure deltas, ready for poisson estimator:"
    print >> sys.stderr, y_dep
    print >> sys.stderr, X_dep

    # Fit poisson distributions for arrivals and departures, print results
    print >> sys.stderr, "Fitting poisson models for arrivals and departures!"
    arr_poisson_model = sm.Poisson(y_arr, X_arr)
    arr_poisson_results = arr_poisson_model.fit()
    
    dep_poisson_model = sm.Poisson(y_dep, X_dep)
    dep_poisson_results = dep_poisson_model.fit()
    
    # Print model results to stdout
    print arr_poisson_results.summary()
    print dep_poisson_results.summary()
    
    poisson_results = {"arrivals": arr_poisson_results, "departures": dep_poisson_results}
    
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
            # If the month is January, month estimate is 0 because January's
            # effect is already reflected in the intercept. The monthly effects
            # are all relative to January. Same for hour of day.
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
    
        # Compute log lambda, which is a linear function of the hour, month, and weekday coefficient estimates
        log_lambda = intercept + month_estimate + hour_estimate + weekday_estimate
        
        # Raise e to log lambda to compute the lambda/expected value of the Poisson distribution for given covariates.
        est_lambda = exp(log_lambda)
        
        return est_lambda
    
    # Create list of hour-chunks in between the current time and the prediction time
    # Need to do this to calculate cumulative lambda rate of arrivals and departures below.
    prediction_time = current_time + prediction_interval

    time_list = [current_time]
    next_step = current_time
    while next_step != prediction_time:
    
        if floor(next_step) + 1 < prediction_time:
            next_step = floor(next_step) + 1
        
        else:
            next_step = prediction_time
            
        time_list.append(next_step)
        
    # Calculate the cumulative lambda rate over the predition interval
    # For arrivals..
    arr_cum_lambda = 0 
    for i in range(1, len(time_list)):
        # Compute arrival lambda for entire current hour
        est_lambda = lambda_calc(month, time_list[ i - 1 ], weekday, poisson_results["arrivals"])

        # Find hour-chunk lambda
        hour_proportion = time_list[i] - time_list[ i - 1 ]
        interval_lambda = est_lambda * hour_proportion
        
        # Count up hour-chunk lambdas to get cumulative lambda
        arr_cum_lambda += interval_lambda
        
    # .. and departures
    dep_cum_lambda = 0 
    for i in range(1, len(time_list)):
        est_lambda = lambda_calc(month, time_list[ i - 1 ], weekday, poisson_results["departures"])
        hour_proportion = time_list[i] - time_list[ i - 1 ]
        interval_lambda = est_lambda * hour_proportion
        
        dep_cum_lambda += interval_lambda
    
    # Subtract cumulative departure lambdas from arrival lambdas to find net lamdas 
    # over the prediction interval
    net_lambda = arr_cum_lambda - dep_cum_lambda
    
    return net_lambda

#<codecell>

# Convert bike availability time series into hourly interval count data
arrival_departure_deltas = find_hourly_arr_dep_deltas(station_updates)

# Remove hourly swings in bike arrivals and departures caused by station rebalancing
rebalancing_data = '/mnt/data1/BikeShare/rebalancing_trips_2_2012_to_3_2013.csv'
clean_arrival_departure_deltas = remove_rebalancing_deltas(arrival_departure_deltas, rebalancing_data, station_id)

# Estimate the poisson point process
print "Poisson results without removing rebalancing trips:"
poisson_results = fit_poisson(arrival_departure_deltas)
print "Poisson results with rebalancing trips removed:"
clean_poisson_results = fit_poisson(clean_arrival_departure_deltas)

# <codecell>

# Try to predict!
current_time = 17.5
prediction_interval = 1
month = 5
weekday = 0

bike_change = predict_net_lambda(current_time, prediction_interval, month, weekday, poisson_results)
print "The predicted change in bikes at time %s and month %s is %s" % (str(floor(current_time)), str(month), str(bike_change))

clean_bike_change = predict_net_lambda(current_time, prediction_interval, month, weekday, clean_poisson_results)
print "The predicted change in bikes (with clean poisson) at time %s and month %s is %s" % (str(floor(current_time)), str(month), str(clean_bike_change))
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


