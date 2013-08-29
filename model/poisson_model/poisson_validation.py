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
from poisson_fit import *

station_id = '17'
time_interval = '1H'
total_station_updates = get_station_data(station_id)
total_arrivals_departures = rebalance_station_poisson_data(total_station_updates, station_id, time_interval, include_rebalance = True)

def fit_poisson_simulation(arrivals_departures):
    
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

def validation_simulation(station_id, starting_time, final_time, max_slots, starting_bikes_available, month, weekday, poisson_results, trials=250):
    bikes_results = [] # numbikes at the station at the end of each trial
    go_empty_results = [] #
    go_full_results = [] #
    for i in range(1,trials):
		bikes, empty, full = simulate_bikes(station_id, starting_time,final_time,max_slots,starting_bikes_available,month,weekday, poisson_results)
		bikes_results.append(bikes)
		go_empty_results.append(empty)
		go_full_results.append(full)
    return (bikes_results, go_empty_results, go_full_results)

def arr_and_dep_until_time(time, total_arrival_departures):
    arrivals_departures = total_arrival_departures[:str(time)]
    return arrivals_departures

def empty_in_window(starting_time, ending_time, total_station_updates):
    go_empty = 0
    bikes_available_in_window = total_station_updates['bikes_available'][str(starting_time):str(ending_time)]
    return int(any(bikes_available_in_window==0))

def bikes_at_time(time, total_station_updates):
    bikes_available_up_to_time = total_station_updates['bikes_available'][str(time):]
    return bikes_available_up_to_time[0]

def mse_calculation(min_time_pt, last_time, months_time_step, days_time_step, hours_time_step, prediction_interval, total_arrival_departures):
    time = min_time_pt
    SE = 0
    SE_IND = 0
    num_comps = 1
    while time < last_time:
    	arrivals_departures_validation = arr_and_dep_until_time(time, total_arrival_departures)
        poisson_results_validation = fit_poisson_simulation(arrivals_departures_validation)
        
        converted_time = round(time.hour + (time.minute / float(60)), 3)
        final_time = time + relativedelta(hours = prediction_interval)
        converted_final_time = round(final_time.hour + (final_time.minute / float(60)), 3)
        
        max_slots = 25
        month = time.month
        weekday = 0
        if (time.isoweekday == 0) or (time.isoweekday == 7):
            weekday = 1
        
        starting_bikes_available = bikes_at_time(time, total_station_updates)
        
        bikes_results, empty_results, full_results = validation_simulation(station_id, converted_time, converted_final_time,  max_slots, starting_bikes_available, month, weekday, poisson_results_validation, 250)
        
        expected_bikes = np.mean(bikes_results)
        prob_empty = np.mean(empty_results)
        
        SE += (expected_bikes - float(bikes_at_time(final_time, total_station_updates)))**2
        SE_IND += (prob_empty - empty_in_window(time, final_time, total_station_updates))**2
        
        time += relativedelta(months = months_time_step, days = days_time_step, hours = hours_time_step)
        num_comps += 1
    
    MSE = SE / num_comps
    MSE_IND = SE_IND / num_comps
    
    return (MSE, MSE_IND)

#print total_station_updates.index[-1]

last_time = datetime(2013, 7, 1, 12,0,0)

# Validate the model!
min_time_pt = datetime(2011, 10, 7,12,38,2)

months_time_step = 0 # number of months time step
days_time_step = 7 # number of days time step
hours_time_step = 1 # number of hours time step

preds = [0.25, 0.5, 0.75, 1.0, 2.0] # Number of Hours Out We Want to Predict
mse_results = []
mse_ind_results = []

for prediction_interval in preds:
    mse, mse_ind = mse_calculation(min_time_pt, last_time, months_time_step, days_time_step, hours_time_step, prediction_interval, total_arrival_departures)
    
    mse_results.append(mse)
    mse_ind_results.append(mse_ind)
    
print mse_results

print mse_ind_results
