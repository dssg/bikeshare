# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>
import sys
import os

import psycopg2
import pandas as pd
from pandas.core.datetools import *
import numpy as np
import math

from binomial_fit_function import binomial_fit
from poisson_fit_function import poisson_fit

def model_validation_poisson(modelfit, n, data, stationid, startdate = None):

    # Set start date of training samples we want to estimate and predict from during rolling window validation.
    if startdate == None:
        startdate = data.index[0]

    else:
        
        try:
            startdate = data[startdate:].index[0]
        
        except:
            print >> sys.stderr, "That date is after the end of biketime. We'll choose the first date in our dataset."
            startdate = data.index[0]

    print >> sys.stderr, "Fixed the start date"        
    
    # Initiate the end date of the training sample.
    enddate = startdate + DateOffset(years=1)

    # Define the offset we'll use to increment the end date of the training sample.
    offset = DateOffset(days=1, hours=1)
    print >> sys.stderr, "Set the offset"

    # Compute mean squared errors.
    # Fit poisson on the first year, predict number of bikes at 15, 30, 45, and 60min 
    # of the first hour of the first year, compute squared errors for each interval.
    # Then move up by a day and hour, refit, predict, and compute errors until we reach
    # present day. Print mean of the squared errors to stdout.
    MSE15 = []
    MSE30 = []
    MSE45 = []
    MSE60 = []
    for i in range(10000):

        # Step forward in time between each round of estimation and prediction.
        if i != 0:
            enddate += offset

        # Get actual bikes at ~15, 30, 45, and 60 min for current, offset day and hour.
        try:
            # Get next 7 15-minute observations after the training data.
            # The interval data that goes into poison is sampled every 2 min,
            # whereas the binomial data is 15, so this is hacky way of making
            # the observations we're trying to predict in our validation comparable.
            actual_bikes_per_15 = data[str(enddate):].iloc[0::8].iloc[1:8]
            predicted_bikes_per_15min = data[str(enddate):].iloc[0::8].iloc[1:8]
           
        except:
            print >> sys.stderr, "Shit! Guess we're done now."
            break

        else:

            print "Training on data up to %s" % str(enddate)
        
            # Get training data for this round of prediction.
            print >> sys.stderr, "Getting training data."
            training_data = data[ str(startdate) : str(enddate) ]
        
            # Fit the model on this training data, return a function that uses
            # coefficient estimates to predict.
            print >> sys.stderr, "Fit the model"
            model = modelfit(training_data, stationid, n)

            # Get next 7 16-minute bike observations after the current end date, use the third
            # of the three observations (30 min ago, 15 min ago, and now) to predict 15 minutes out
            # - two previous time lags are there because of the other model.
            # Use this predicted number of bikes and bikes now/15 min ago to predict 30 min out.
            # Do this until you predict up to the hour. Poisson only uses the current number 
            # of bikes to predict, no time lags.
            print "Steps Out, Expected Number of Bikes, Actual Number of Bikes, MSE"

            # Predict bikes in next 15, 30, 45, and 60 minutes, and compute squared error relative to actual number of bikes.
            for i in range(4):

                # Predict expected value of bikes at current time
                ev_bikes = model(predicted_bikes_per_15min.iloc[ i : (i + 3 )], n)
                ev_slots = n - ev_bikes

                # Save predicted expected value of bikes to the corresponding 15-min slot in the 
                # predicted bikes dataframe.                
                predicted_bikes_per_15min.iloc[ i + 3 ]["bikes_available"] = ev_bikes
                predicted_bikes_per_15min.iloc[ i + 3 ]["slots_available"] = ev_slots

                # Fetch the true number of bikes at each 15-minute time step.
                true_bikes = actual_bikes_per_15.iloc[ i + 3 ]["bikes_available"]
                
                # Compute squared error between the predicted number of bikes and the actual
                # number 15 then 30, 45, and 60 minutes from now.
                mse = pow((ev_bikes - true_bikes), 2)

                if i == 0:
                    MSE15.append(mse)

                elif i == 1:
                    MSE30.append(mse)

                elif i == 2:
                    MSE45.append(mse)

                elif i == 3:
                    MSE60.append(mse)

                print >> sys.stderr, "%d, %f, %d, %f" % (i, ev_bikes, true_bikes, mse)
            
    print "Mean Squared Error at 15 minutes out %f" % (sum(MSE15) / len(MSE15)) 
    print "Mean Squared Error at 30 minutes out %f" % (sum(MSE30) / len(MSE30)) 
    print "Mean Squared Error at 45 minutes out %f" % (sum(MSE45) / len(MSE45)) 
    print "Mean Squared Error at 60 minutes out %f" % (sum(MSE60) / len(MSE60)) 

def no_nan(lst):
    return [x for x in lst if math.isnan(x) == False]

def model_validation_binomial(modelfit, n, data, startdate = None):
    # Set start date of training samples we want to estimate and predict from during rolling window validation.
    if startdate == None:
        startdate = data.index[0]

    else:
        
        try:
            startdate = data[startdate:].index[0]
        
        except:
            print >> sys.stderr, "That date is after the end of biketime. We'll choose the first date in our dataset."
            startdate = data.index[0]

    print >> sys.stderr, "Fixed the start date"        
    
    # Initiate the end date of the training sample.
    enddate = startdate + DateOffset(years=1)

    # Define the offset we'll use to increment the end date of the training sample.
    offset = DateOffset(days=1, hours=1)
    print >> sys.stderr, "Set the offset"

    # Compute mean squared errors.
    # Fit binomial model on the first year, predict number of bikes at 15, 30, 45, and 60min 
    # of the first hour of the first year, compute squared errors for each interval.
    # Then move up by a day and hour, refit, predict, and compute errors until we reach
    # present day. Print mean of the squared errors to stdout.
    MSE15 = []
    MSE30 = []
    MSE45 = []
    MSE60 = []
    for i in range(10000):

        # Step forward in time between each round of estimation and prediction.
        if i != 0:
            enddate += offset
        
        # Get actual bikes at ~15, 30, 45, and 60 min for current, offset day and hour.
        try:
            predicted_bikes_per_15min = data[str(enddate):].iloc[1:8]
            actual_bikes_per_15 = data[str(enddate):].iloc[1:8]

        except:
            print >> sys.stderr, "Guess we're done now."
            break

        else:
            print "Training on data up to %s" % str(enddate)
        
            # Get training data for this round of prediction.
            print >> sys.stderr, "Getting training data."
            training_data = data[ str(startdate) : str(enddate) ]

            # Get next 7 16-minute bike observations after the current end date, use the first
            # three observations (30 min ago, 15 min ago, and now) to predict 15 minutes out.
            # Use this predicted number of bikes and bikes now/15 min ago to predict 30 min out.
            # Do this until you predict up to the hour.
            print "Steps Out, Expected Number of Bikes, Actual Number of Bikes, MSE"

            # Predict bikes in next 15, 30, 45, and 60 minutes, and compute squared error relative to actual number of bikes.
            for i in range(4):

                # Predict expected value of bikes at current time
                lst_prob, ev_bikes = model(predicted_bikes_per_15min.iloc[ i : (i + 3)], n)
                ev_slots = n - ev_bikes

                # Save predicted expected value of bikes to the corresponding 15-min slot in the 
                # predicted bikes dataframe.
                predicted_bikes_per_15min.iloc[ i + 3 ]["bikes_available"] = ev_bikes
                predicted_bikes_per_15min.iloc[ i + 3 ]["slots_available"] = ev_slots

                # Fetch the true number of bikes at each 15-minute time step.
                true_bikes = actual_bikes_per_15.iloc[i+3]["bikes_available"]

                # Compute squared error between the predicted number of bikes and the actual
                # number 15 then 30, 45, and 60 minutes from now.
                mse = pow((ev_bikes - true_bikes),2)

                if i == 0: 
                    MSE15.append(mse)

                elif i == 1:
                    MSE30.append(mse)

                elif i == 2: 
                    MSE45.append(mse)

                elif i ==3: 
                   MSE60.append(mse)
                print "%d, %f, %d, %f" % (i,ev_bikes,true_bikes,mse)
        
    
    print "Mean Squared Error at 15 minutes out %f" % (sum(no_nan(MSE15)) / len(no_nan(MSE15)))
    print "Mean Squared Error at 30 minutes out %f" % (sum(no_nan(MSE30)) / len(no_nan(MSE30)))
    print "Mean Squared Error at 45 minutes out %f" % (sum(no_nan(MSE45)) / len(no_nan(MSE45)))
    print "Mean Squared Error at 60 minutes out %f" % (sum(no_nan(MSE60)) / len(no_nan(MSE60)))


if __name__ == '__main__':

    # Set the station you want run sliding window validation on,
    # and the data you want to start fitting from.
    station_id = 17
    start_date = "02/16/2012"

    model = sys.argv[1]
    model = model.lower()

    if model == "poisson":

        # Connect to postgres database
        conn = psycopg2.connect("dbname="+os.environ.get('dbname')+" user="+os.environ.get('dbuser') + " host="+os.environ.get('dburl'))
        cur = conn.cursor()

        # Get 2-min station bike availability data
        print >> sys.stderr, "Getting data for station."
        cur.execute("SELECT * FROM bike_ind_washingtondc WHERE tfl_id = " + str(station_id) + ";")
        station_data = cur.fetchall()

        # Add data to dataframe, add timezone
        dc_station_17_poisson = pd.DataFrame.from_records(station_data, columns = ["station_id", "bikes_available", "slots_available", "timestamp"], index = "timestamp")
        dc_station_17_poisson.index = dc_station_17_poisson.index.tz_localize('UTC').tz_convert('US/Eastern')

        # Measure predictive accuracy of poisson model using sliding window validation.
        print >> sys.stderr, "Running model validation script for poisson."
        model_validation_poisson(poisson_fit, 25, dc_station_17_poisson, station_id, start_date)

# <codecell>
    elif model == "binomial":

        # Get 15-min station bike availability data, binomial model fits every 15 minutes.
        from fetch_station import fetch_station
        dc_station_17_binomial = fetch_station("Washington, D.C.", station_id, 15)

        # Measure predictive accuracy of binomial model using sliding window validation.
        print >> sys.stderr, "Running model validation script for binomial."
        model_validation_binomial(binomial_fit, 25, dc_station_17_binomial, start_date)

    else:
        print >> sys.stderr, "Don't know how to validate that model!"

