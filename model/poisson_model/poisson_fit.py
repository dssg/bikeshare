import os
import psycopg2
import numpy as np
import pandas as pd
import patsy
import statsmodels.api as sm
import pickle
import random
import math
from datetime import *
import pytz
from dateutil.relativedelta import *
from dateutil.parser import parse
import calendar
from poisson_data_extract import *

def fit_poisson(station_id, include_rebalance = False, initial_time = datetime(2001,1,1), final_time = datetime(2020,1,1), time_interval = '1H'):
    # Use the correct delta data
    station_updates = get_station_data(station_id)

    arrivals_departures = rebalance_station_poisson_data(station_updates, station_id, time_interval, include_rebalance = False)
   
    # Create design matrix for months, hours, and weekday vs. weekend.
    # We can't just create a "month" column to toss into our model, because it doesnt
    # understand what "June" is. Instead, we need to create a column for each month
    # and code each row according to what month it's in. Ditto for hours and weekday (=1).
    
    y_arr, X_arr = patsy.dmatrices("arrivals ~ C(months, Treatment) + C(hours, Treatment) + C(weekday_dummy, Treatment)", arrivals_departures, return_type='dataframe')
    y_dep, X_dep = patsy.dmatrices("departures ~ C(months, Treatment) + C(hours, Treatment) + C(weekday_dummy, Treatment)", arrivals_departures, return_type='dataframe')

    y_dep[pd.isnull(y_dep)] = 0
    
    # Fit poisson distributions for arrivals and departures, print results
    arr_poisson_model = sm.Poisson(y_arr, X_arr)
    arr_poisson_results = arr_poisson_model.fit(disp=0)
    
    dep_poisson_model = sm.Poisson(y_dep, X_dep)
    dep_poisson_results = dep_poisson_model.fit(disp = 0)
    
    # print arr_poisson_results.summary(), dep_poisson_results.summary()
    
    poisson_results = [arr_poisson_results, dep_poisson_results]
    
    return poisson_results

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

def lambda_calc(month, time, weekday, poisson_results):
    "Compute the lambda value for a specific month, time (hour), and weekday."
        
    # Pull out coefficient estimates for the factored covariants
    #estimates = poisson_results["params"]
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
    if (hour == 0) or (hour == 24):
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
    

def predict_net_lambda(current_time, prediction_interval, month, weekday, poisson_results):
    
    # Define function that takes in a month, time, weekday and returns 
    # a lambda - the expected value of arrivals or departures during that hour (given that month)
    # - using the covariate coefficients estimated above.
    
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

def distinctIds():
    # Returns the Distinct Station IDs for Washington DC dataset
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT id FROM metadata_washingtondc order by id;")
    station_ids = cur.fetchall()

    station_list = []
    for station in station_ids:
        station_list.append(station[0])
        
    return station_list

def save_poisson_results(include_rebalance = False):
    # Runs the Poisson Fit Code for Each of the Station IDs
    station_ids = distinctIds()
    tag = "rebalanced"
    if (include_rebalance == False):
        tag = "notrebalanced"

    for station_id in station_ids:
        poisson_results = fit_poisson(station_id, include_rebalance)
        file_out = open("/mnt/data1/BikeShare/pickles/poisson_results_%s_%s.p" % (station_id, tag), "wb")
        to_save_ps = (poisson_results[0].params, poisson_results[1].params)
        pickle.dump(to_save_ps, file_out)
        file_out.close()
        print "did %s" % station_id

save_poisson_results(include_rebalance = True)
save_poisson_results(include_rebalance = False)

def load_poisson_result(station_id, include_rebalance = False):
    tag = "rebalanced"
    if (include_rebalance == False):
        tag = "notrebalanced"
    temp = pickle.load(open("/mnt/data1/BikeShare/pickles/poisson_results_%s_%s.p" % (station_id,tag), "rb"))
    return (dict(params=temp[0]), dict(params=temp[1]))

def simulate_bikes(station_id, starting_time, final_time, max_slots, starting_bikes_available, month, weekday, poisson_results):
    # Creates a simulated version of the bike counts from starting_time to final_time for
    # station_id with max_slots, and a given starting number of bikes

    bikes_available = starting_bikes_available
    current_time = starting_time
    go_empty = 0
    go_full = 0
    while current_time < final_time:
        # Calculate the Appropriate Up and Down Rate Terms
        up_lambda = lambda_calc(month,current_time,weekday, poisson_results[0])
        down_lambda = lambda_calc(month,current_time,weekday, poisson_results[1])
        total_lambda = float(up_lambda + down_lambda)

        next_obs_time = random.expovariate(total_lambda)
        chance_up = up_lambda / total_lambda

        # Update the Current Time to the Next Observation Time
        current_time += next_obs_time       

        if current_time < final_time:

            if random.uniform(0,1) > chance_up:
                bikes_available -= 1
            else:
                bikes_available += 1

        # Adjust Bikes Available to Sit Inside Range
        if bikes_available < 0:
            bikes_available = 0
        elif bikes_available > max_slots:
            bikes_available = max_slots

        if bikes_available == 0:
            go_empty = 1
        if bikes_available == max_slots:
            go_full = 1

    return (bikes_available, go_empty, go_full)


def simulation(station_id, starting_time, final_time, max_slots, starting_bikes_available, month, weekday, simulate_bikes, trials=250, include_rebalance = False):
    # Produces multiple simulated hours and records the final number of bikes
    # along with information regarding whether the station ever goes empty or
    # full in the time interval.

    poisson_results = load_poisson_result(station_id, include_rebalance)
    bikes_results = [] # numbikes at the station at the end of each trial
    go_empty_results = [] #
    go_full_results = [] #
    for i in range(1,trials):
        bikes, empty, full = simulate_bikes(station_id, starting_time,final_time,max_slots,starting_bikes_available,month,weekday, poisson_results)
        bikes_results.append(bikes)
        go_empty_results.append(empty)
        go_full_results.append(full)
    return (bikes_results, go_empty_results, go_full_results)
