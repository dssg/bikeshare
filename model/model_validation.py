# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>
import sys
import pandas as pd
from pandas.core.datetools import *
import numpy as np
import psycopg2
import os
from binomial_fit_function import binomial_fit
from poisson_fit_function import poisson_fit

def model_validation(modelfit, n, data, stationid, startdate = None, modeltype=None):
    if startdate == None:
        startdate = data.index[0]
    else:
        try:
            startdate = data[startdate:].index[0]
        except:
            print >> sys.stderr, "That date is after the end of biketime. We'll choose the first date in our dataset."
            startdate = data.index[0]
    print >> sys.stderr, "Fixed the start date"        
    enddate = startdate + DateOffset(years=1)
    offset = DateOffset(days=1, hours=1)
    print >> sys.stderr, "Set the offset"
    MSE15 = []
    MSE30 = []
    MSE45 = []
    MSE60 = []
    for i in range(10000):
        if i != 0:
            enddate += offset
            print >> sys.stderr, "Step forward in time"
        try:
           print >> sys.stderr, "%s" % data[str(enddate):].head()
	   if modeltype == "poisson":
		test_data = data[str(enddate):].iloc[0::8].iloc[1:8]
		true_test_data = data[str(enddate):].iloc[0::8].iloc[1:8]
           else:
		test_data = data[str(enddate):].iloc[1:8]
            	print >> sys.stderr, "Established test data"
            	true_test_data = data[str(enddate):].iloc[1:8]
            	print >> sys.stderr, "Oh phew! We can still test more points"
        except:
            print >> sys.stderr, "Shit! Guess we're done now."
            break
        else:
            print "Training on data up to %s" % str(enddate)
        
        fit_data = data[str(startdate):str(enddate)]
        print >> sys.stderr, "Set the fit data"
        model = modelfit(fit_data, stationid, n)
        print >> sys.stderr, "Fit the model"
        print "Steps Out, Expected Number of Bikes,  True Expected Number of Bikes, MSE"
        for i in range(4):
            lst_prob,ev_bikes = model(test_data.iloc[i:( i + 3 )], n)
            ev_slots = n - ev_bikes
            test_data.iloc[ i + 3 ]["bikes_available"] = ev_bikes
            test_data.iloc[ i + 3 ]["slots_available"] = ev_slots
            true_bikes = true_test_data.iloc[ i + 3 ]["bikes_available"]
            mse = pow((ev_bikes-true_bikes), 2)
	   
	    if i == 0:
		MSE15.append(mse)
           
	    elif i == 1:
		MSE30.append(mse)
            
            elif i == 2:
		MSE45.append(mse)
            
            elif i ==3:
		MSE60.append(mse)
            print >> sys.stderr, "%d,%f,%d,%f" % (i, ev_bikes, true_bikes, mse)
            
    print "Mean Squared Error at 15 minutes out %f" % (sum(MSE15) / len(MSE15)) 
    print "Mean Squared Error at 30 minutes out %f" % (sum(MSE30) / len(MSE30)) 
    print "Mean Squared Error at 45 minutes out %f" % (sum(MSE45) / len(MSE45)) 
    print "Mean Squared Error at 60 minutes out %f" % (sum(MSE60) / len(MSE60)) 


import pandas as pd
from pandas.core.datetools import *
import numpy as np
from binomial_fit_function import binomial_fit
import math

def no_nan(lst):
    return [x for x in lst if math.isnan(x) == False]

def model_validation_binomial(modelfit, n, data, startdate = None):
    if startdate == None:
        startdate = data.index[0]
    else:
        try:
            startdate = data[startdate:].index[0]
        except:
            print "That date is after the end of biketime. We'll choose the first date in our dataset."
            startdate = data.index[0]
            
    enddate = startdate + DateOffset(years=1)
    offset = DateOffset(days=1, hours =1)
    MSE15 = []
    MSE30 = []
    MSE45 = []
    MSE60 = []
    for i in range(10000):
        if i !=0:
            enddate += offset
            
        try:
            test_data = data[str(enddate):].iloc[1:8]
            true_test_data = data[str(enddate):].iloc[1:8]
        except:
            break
        else:
            print "Training on data up to %s" % str(enddate)
        
        fit_data = data[str(startdate):str(enddate)]
        model = modelfit(fit_data,n = None)
        #print "Steps Out, Expected Number of Bikes,  True Expected Number of Bikes, MSE"
        for i in range(4):
            lst_prob,ev_bikes = model(test_data.iloc[i:(i+3)],n)
            ev_slots = n-ev_bikes
            test_data.iloc[i+3]["bikes_available"] = ev_bikes
            test_data.iloc[i+3]["slots_available"] = ev_slots
            true_bikes = true_test_data.iloc[i+3]["bikes_available"]
            mse = pow((ev_bikes-true_bikes),2)
            if i == 0: 
                MSE15.append(mse)

            elif i == 1:
                MSE30.append(mse)

            elif i == 2: 
                MSE45.append(mse)

            elif i ==3: 
               MSE60.append(mse)
            print "%d,%f,%d,%f" % (i,ev_bikes,true_bikes,mse)
    
    

    
    print "Mean Squared Error at 15 minutes out %f" % (sum(no_nan(MSE15)) / len(no_nan(MSE15)))
    print "Mean Squared Error at 30 minutes out %f" % (sum(no_nan(MSE30)) / len(no_nan(MSE30)))
    print "Mean Squared Error at 45 minutes out %f" % (sum(no_nan(MSE45)) / len(no_nan(MSE45)))
    print "Mean Squared Error at 60 minutes out %f" % (sum(no_nan(MSE60)) / len(no_nan(MSE60)))


if __name__ == '__main__':

    start_date = "02/16/2012"
    station_id = 17

    model = sys.argv[1]
    model = model.lower()

    if model == "poisson":

        conn = psycopg2.connect("dbname="+os.environ.get('dbname')+" user="+os.environ.get('dbuser') + " host="+os.environ.get('dburl'))
        cur = conn.cursor()

        print >> sys.stderr, "Getting data for station."
        cur.execute("SELECT * FROM bike_ind_washingtondc WHERE tfl_id = " + str(station_id) + ";")
        station_data = cur.fetchall()

        # Add data to dataframe, add timezone
        dc_station_17_poisson = pd.DataFrame.from_records(station_data, columns = ["station_id", "bikes_available", "slots_available", "timestamp"], index = "timestamp")
        dc_station_17_poisson.index = dc_station_17_poisson.index.tz_localize('UTC').tz_convert('US/Eastern')

        print >> sys.stderr, "Running model validation script for poisson."
        model_validation(poisson_fit, 25, dc_station_17_poisson, station_id, start_date, modeltype = "poisson")

# <codecell>
    elif model == "binomial":

        from fetch_station import fetch_station
        dc_station_17_binomial = fetch_station("Washington, D.C.", station_id, 15, 'max')

        print >> sys.stderr, "Running model validation script for binomial."
        model_validation_binomial(binomial_fit, 25, dc_station_17_binomial, start_date)

    else:
        print >> sys.stderr, "Can't validate that model!"

