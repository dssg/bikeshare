# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

import os
import psycopg2
import numpy as np
import pandas as pd
import patsy
import statsmodels.api as sm
import pickle
import random
from math import floor, exp
from datetime import *
import pytz
from dateutil.relativedelta import *
import calendar
from config import config

# Connect to postgres db
# conn = psycopg2.connect("dbname= %s user= %s host=%s" % (config()["DB"], config()["USER"], config()["DB_URL"]))
# <codecell>

def get_station_data(station_id):
    # Pulls Data for Given Station_id and Converts to Pandas Dataframe
    cur = conn.cursor()

    # Fetch data for station 17 in Washington, DC - 16th & Harvard St NW, terminalName: 31103
    cur.execute("SELECT * FROM bike_ind_washingtondc WHERE tfl_id = %s;" % station_id)
    station_data = cur.fetchall()

    # Put data in pandas dataframe
    station_updates = pd.DataFrame.from_records(station_data, columns = ["station_id", "bikes_available", "spaces_available", "timestamp"], index = "timestamp")

    # Convert UTC timezone of the timestamps to DC's Eastern time
    station_updates.index = station_updates.index.tz_localize('UTC').tz_convert('US/Eastern')

    return station_updates

# <codecell>

def fit_poisson(station_updates):

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

    arrivals_departures = pd.DataFrame(arrivals, columns=["arrivals"])
    arrivals_departures['departures'] = departures
    
    # Extract months for Month feature, add to model data
    delta_months = arrivals_departures.index.month
    arrivals_departures['months'] = delta_months

    # Extract hours for Hour feature
    delta_hours = arrivals_departures.index.hour
    arrivals_departures['hours'] = delta_hours

    # Extract weekday vs. weekend variable
    delta_dayofweek = arrivals_departures.index.weekday

    delta_weekday_dummy = delta_dayofweek.copy()
    delta_weekday_dummy[delta_dayofweek < 5] = 1
    delta_weekday_dummy[delta_dayofweek >= 5] = 0

    arrivals_departures['weekday_dummy'] = delta_weekday_dummy

    # print arrivals_departures
    # print arrivals_departures.head(20)
    
    # Create design matrix for months, hours, and weekday vs. weekend.
    # We can't just create a "month" column to toss into our model, because it doesnt
    # understand what "June" is. Instead, we need to create a column for each month
    # and code each row according to what month it's in. Ditto for hours and weekday (=1).
    
    y_arr, X_arr = patsy.dmatrices("arrivals ~ C(months, Treatment) + C(hours, Treatment) + C(weekday_dummy, Treatment)", arrivals_departures, return_type='dataframe')
    y_dep, X_dep = patsy.dmatrices("departures ~ C(months, Treatment) + C(hours, Treatment) + C(weekday_dummy, Treatment)", arrivals_departures, return_type='dataframe')

    y_dep[pd.isnull(y_dep)] = 0
    
    # Fit poisson distributions for arrivals and departures, print results
    arr_poisson_model = sm.Poisson(y_arr, X_arr)
    arr_poisson_results = arr_poisson_model.fit()
    
    dep_poisson_model = sm.Poisson(y_dep, X_dep)
    dep_poisson_results = dep_poisson_model.fit()
    
    # print arr_poisson_results.summary(), dep_poisson_results.summary()
    
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

def lambda_calc(month, time, weekday, poisson_results):
    "Compute the lambda value for a specific month, time (hour), and weekday."
        
    # Pull out coefficient estimates for the factored covariants
    estimates = poisson_results["params"]
    
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

# <codecell>

# Estimate the poisson!
def save_poisson_results():
    print ("saving")
    # station_ids = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74]
    # station_ids = getStations()
    for station in station_ids:
        station_id = station[0]
        if (os.path.isfile("%spoisson_results_%s.p" % (pickle_folder, station_id))):
            continue
        station_updates = get_station_data(station_id)
        print("Got data, now fitting")
        poisson_results = fit_poisson(station_updates)

        file_out = open("%spoisson_results_%s.p" % (pickle_folder, station_id), "wb")
        to_save_ps = (poisson_results[0].params, poisson_results[1].params)
        pickle.dump(to_save_ps, file_out)
        file_out.close()
        print "finished %s" % station_id
    print("done saving")
        
# <codecell>
pickle_folder = "/mnt/data1/BikeShare/pickles/"
# pickle_folder = "/Users/darkzeroman/dssg/bikeshare/web/static/pickles/"

# save_poisson_results()

def load_poisson_result(station_id):
    temp = pickle.load(open("%spoisson_results_%s.p" % (pickle_folder, station_id), "rb"))
    return (dict(params=temp[0]), dict(params=temp[1]))

# <codecell>

'''
# Auxiliary code
# Try to predict!
current_time = 17.5
prediction_interval = 1
month = 5
weekday = 0

bike_change = predict_net_lambda(current_time, prediction_interval, month, weekday, poisson_results)
# print "The change in bikes at time %s and month %s is %s" % (str(floor(current_time)), str(month), str(bike_change))

# Plot predictions of available bikes by hour for given covariates
init_bikes = 18
bike = init_bikes
bikes = [init_bikes]
hours_of_day  = range(1,24)

for hour in hours_of_day:
    bike += predict_net_lambda(hour, prediction_interval, month, weekday, poisson_results)
    bikes.append(bike)
       
pd.Series(bikes).plot()
'''

# <codecell>

# Validate the model!
# min_time_pt = datetime.datetime(2010,10,8)
# prediction_interval =
# time_step =

#def validate_model(min_time_pt):
    
    # Generate list of time points incremented by the time_step
    
    # Get observations before timepoint
#    smaller_updates = station_updates[station_updates.index < min_time_pt]
    
#    print station_updates
#    print smaller_updates

#validate_model(min_time_pt)

# <codecell>

# Simulate bike availability at station 17 for next half hour

# We're doing this to flag when station is full or empty, which
# is what bikeshare operators want.

#import sys 

def simulate_bikes(station_id, starting_time, final_time, max_slots, starting_bikes_available, month, weekday, poisson_results):
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


def simulation(station_id, starting_time, final_time, max_slots, starting_bikes_available, month, weekday, simulate_bikes, trials=250):
    poisson_results = load_poisson_result(station_id)
    bikes_results = [] # numbikes at the station at the end of each trial
    go_empty_results = [] #
    go_full_results = [] #
    for i in range(1,trials):
        bikes, empty, full = simulate_bikes(station_id, starting_time,final_time,max_slots,starting_bikes_available,month,weekday, poisson_results)
        bikes_results.append(bikes)
        go_empty_results.append(empty)
        go_full_results.append(full)
    return (bikes_results, go_empty_results, go_full_results)

# <codecell>

def make_prediction(station, how_many_mins):
    try:
        station_id = station[0]
        starting_datetime = datetime.now(pytz.timezone('US/Eastern'))
        ending_datetime = starting_datetime + relativedelta(minutes=how_many_mins)

        
        # protect sql injection later?
        cur = conn.cursor()
        cur.execute("select * from bike_ind_washingtondc where tfl_id = %s order by timestamp desc limit 1;" % station_id)

        _, starting_bikes_available, num_spaces, _  = cur.fetchall()[0] #(station_id, bikes, spaces, timestamp)

        max_slots = starting_bikes_available + num_spaces
        
        month = starting_datetime.month # Between 1-12
        
        weekday = 0
        if (starting_datetime.isoweekday == 0) or (starting_datetime.isoweekday == 7):
            weekday = 1
        
        starting_time = round(starting_datetime.hour + (starting_datetime.minute / float(60)), 3)
        ending_time = round(ending_datetime.hour + (ending_datetime.minute / float(60)), 3)
        
        bikes_results, empty_results, full_results = simulation(station_id, starting_time, ending_time, max_slots, \
            starting_bikes_available, month, weekday, simulate_bikes, 250)
        
        week_dict = {'0': 'Week', '1' : 'Weekend'}

        # net_lambda = predict_net_lambda(starting_time, final_time - starting_time, month, weekday, poisson_results)
        
        # print ("In %s during the %s" % (calendar.month_name[month], week_dict[str(weekday)]))
        # print ("For Starting Time: %0.2f and Ending Time: %0.2f with Initial Bikes: %d out of a Maximum: %d" % (starting_time, ending_time, starting_bikes_available, max_slots))
        # print ('Expected Number of Bikes at %s: %0.2f' % (ending_time, round(np.mean(bikes_results),2)))
        # print 'Other Expected Value : ', starting_bikes_available + net_lambda
        # print ('Probability of Being (Empty, Full) Any Time in the Next %0.2f hours: (%0.2f, %0.2f)' % \
            # (ending_time - starting_time, round(np.mean(empty_results),2), round(np.mean(full_results),2)))
        print ", ".join(map(str, [how_many_mins, station_id]))
        temp_res = (int(station_id), round(np.mean(bikes_results),2), round(np.mean(empty_results),2), \
            round(np.mean(full_results),2), station[2], station[3], station[1], starting_bikes_available, max_slots)
        res_names = ("station_id", "expected_num_bikes", "prob_empty", "prob_full", "lat", "lon", "name", "current_bikes", "max_slots")
        return dict(zip(res_names, temp_res))
    except KeyError:
        return (int(station_id), "Prediction Error")
# %time make_prediction('17', 15*4)

# <codecell>

def run_code():
    
    starting_time = 6.0
    final_time = 6.5
    starting_bikes_available = 21
    max_slots = 25
    
    month = 8
    weekday = 0
    
    station_id = '17'

    #starting_time, final_time, max_slots, starting_bikes_available, month, weekday,
    
    bikes_results, empty_results, full_results = simulation(station_id, starting_time, final_time, max_slots, starting_bikes_available, \
        month, weekday,simulate_bikes, 500)
    
    expected_num_bikes = round(np.mean(bikes_results), 2)
    prob_empty_any_time = round(np.mean(empty_results), 2)
    prob_full_any_time = round(np.mean(full_results), 2)
    
    #print (expected_num_bikes, prob_empty_any_time, prob_full_any_time)
    
# %timeit run_code()

# <codecell>

def getStations():
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT * FROM metadata_washingtondc order by id;")
    station_ids = cur.fetchall()

    station_list = []
    for station in station_ids:
        station_list.append(station)
        
    return station_list

# print getIds()