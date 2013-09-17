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

conn = psycopg2.connect(dbname=os.environ.get('dbname'), user=os.environ.get('dbuser'), host=os.environ.get('dburl'))

def get_station_data(station_id, initial_time = datetime(2001,1,1), final_time = datetime(2020,1,1)):
    # Pulls Data for Given Station_id and Converts to Pandas Dataframe
    cur = conn.cursor()

    # Fetch data for station 17 in Washington, DC - 16th & Harvard St NW, terminalName: 31103
    cur.execute("SELECT * FROM bike_ind_washingtondc WHERE tfl_id = %s;" % station_id)
    station_data = cur.fetchall()

    # Put data in pandas dataframe
    station_updates = pd.DataFrame.from_records(station_data, columns = ["station_id", "bikes_available", "spaces_available", "timestamp"], index = "timestamp")

    # Convert UTC timezone of the timestamps to DC's Eastern time
    station_updates.index = station_updates.index.tz_localize('UTC').tz_convert('US/Eastern')

    station_updates = station_updates[str(initial_time):str(final_time)]
    return station_updates

def calc_non_rebalance_change(station_number, time_interval):
    # Extracts the rebalancing data for a given station in Washington D.C. with
    # a specific time interval.  Ex. (17, '1H') returns all changes due to rebalancing
    # at station 17 for one hour intervals

    # Read in Rebalancing Data from Instance
    rebalance = pd.io.parsers.read_csv("/mnt/data1/BikeShare/dc_rebalancing.csv", delimiter=",", parse_dates = [5])
    rebalance.columns = ['tech_num','start_station','start_terminal','end_station','end_terminal','start_date','end_date','last_technician_activity','duration','status_reason','bike_num']
    # Note: end_date has missing values, so it was not read in as a timestamp. 
    # This doesn't really matter right now, and we change it into a timestamp later once the missing values are dropped

    # read in crosswalk data
    xwalk = pd.io.parsers.read_csv("/mnt/data1/BikeShare/tfl_id_crosswalk.csv", delimiter = ",", names = ['start_tfl_id','start_terminal'])

    # merge on ids of start station
    rebalance_with_ids_start = pd.merge(rebalance, xwalk, on='start_terminal')

    start_deltas = rebalance_with_ids_start.ix[:,['start_tfl_id','start_date']]
    start_deltas.columns = ['tfl_id','timestamp']
    start_deltas['delta'] = 1
    start = start_deltas.set_index(start_deltas['timestamp'])

    # rename columns in order to merge on ids of end station
    xwalk.columns = ['end_tfl_id','end_terminal']

    # merge on ids of end station
    rebalance_with_ids_end = pd.merge(rebalance_with_ids_start, xwalk, on = 'end_terminal')
    end_deltas = rebalance_with_ids_end.ix[:,['end_tfl_id','end_date']]
    end_deltas.columns = ['tfl_id','timestamp']
    # change timestamp variable to be datetime type (there are no missing values now, so it converts easily)
    end_deltas['timestamp'] = pd.to_datetime(end_deltas['timestamp'])
    end_deltas['delta'] = -1
    end = end_deltas.set_index(end_deltas['timestamp'])

    # Concatenate dataframes with deltas
    deltas = pd.concat([start,end])
    
    # Extract a certain station
    deltas_station = deltas.ix[deltas['tfl_id'] == station_number,:]
    time_interval = time_interval
    agg = deltas_station['delta'].resample(time_interval, how ='sum')

    # Fill in missing values with zeroes 
    agg_no_NaNs = agg.fillna(0)
    return agg_no_NaNs

def rebalance_station_poisson_data(station_updates, station_id, time_interval, include_rebalance = False):
    # Find changes (deltas) in bike count
    bikes_available = station_updates.bikes_available

    # Calculate the Changes in Bikes
    deltas = bikes_available - bikes_available.shift()

    # Include Rebalancing Data and Limit Observations to Window where Rebalancing Data Exists
    if (include_rebalance == True):
        rebalances = calc_non_rebalance_change(int(station_id), '1H')
        rebalances.index = rebalances.index.tz_localize('UTC').tz_convert('US/Eastern')
        minimum_rebalance_data = min(rebalances.index)
        
        # Separate Departure and Arrival of Rebalancing Bikes

        pos_adj_for_rebalances = rebalances[rebalances < 0]
        neg_adj_for_rebalances = rebalances[rebalances > 0]

        pos_deltas = deltas[deltas > 0]
        neg_deltas = deltas[deltas < 0]

        pos_interval_counts_null = pos_deltas.resample(time_interval, how ='sum')
        neg_interval_counts_null = neg_deltas.resample(time_interval, how ='sum')

        pos_interval_counts = pos_interval_counts_null.fillna(0)
        neg_interval_counts = neg_interval_counts_null.fillna(0)

        # Add the Rebalance Data to the Arrival and Departure Data
        # Can cause arrivals to become departures and vice versa.

        rebalanced_pos_deltas_interval_unadj = pos_interval_counts.add(pos_adj_for_rebalances, fill_value=0)
        rebalanced_neg_deltas_interval_unadj = neg_interval_counts.add(neg_adj_for_rebalances, fill_value=0)


        # Identify the Cases where rebalance causes aggregate positives to become negative and
        # adjust departure numbers.

        pos_to_neg_deltas_interval = rebalanced_pos_deltas_interval_unadj[rebalanced_pos_deltas_interval_unadj < 0]
        neg_to_pos_deltas_interval = rebalanced_neg_deltas_interval_unadj[rebalanced_neg_deltas_interval_unadj > 0]

        # print pos_to_neg_deltas_interval.head()
        # print neg_to_pos_deltas_interval.head()

        # These are the good cases we want to keep.  We will then match pos-pos and neg-pos into one 
        # combined vector of all positive deltas.

        pos_to_pos_deltas_interval = rebalanced_pos_deltas_interval_unadj[rebalanced_pos_deltas_interval_unadj > 0]
        neg_to_neg_deltas_interval = rebalanced_neg_deltas_interval_unadj[rebalanced_neg_deltas_interval_unadj < 0]

        rebalanced_pos_deltas_interval_adj = pos_to_pos_deltas_interval.add(neg_to_pos_deltas_interval, fill_value=0)
        rebalanced_neg_deltas_interval_adj = neg_to_neg_deltas_interval.add(pos_to_neg_deltas_interval, fill_value=0)

        # The adjusted numbers do not contain the hours where we observe zero arrivals or departures
        # We use resampling to fix this issue and then fill in the resulting NaN values.

        rebalanced_pos_deltas_interval = rebalanced_pos_deltas_interval_adj.resample(time_interval, how ='sum')
        rebalanced_neg_deltas_interval = rebalanced_neg_deltas_interval_adj.resample(time_interval, how ='sum')

        arrivals = rebalanced_pos_deltas_interval.fillna(0)
        departures = abs(rebalanced_neg_deltas_interval.fillna(0))
    else:
        # If we don't wish to use rebalancing data #
        
        # Separate positive and negative deltas
        pos_deltas = deltas[deltas > 0]
        neg_deltas = abs(deltas[deltas < 0])

        # Count the number of positive and negative deltas per half hour per day, add them to new dataframe.
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

    return arrivals_departures
