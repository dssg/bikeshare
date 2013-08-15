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

def model_validation(modelfit, n, data, stationid, startdate = None):
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
    for i in range(10000):
        if i != 0:
            enddate += offset
            print >> sys.stderr, "Step forward in time"
        try:
            print >> sys.stderr, "%s" % data[str(enddate):].head()
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
        for i in range(3):
            lst_prob,ev_bikes = model(test_data.iloc[i:( i + 3 )], n)
            ev_slots = n - ev_bikes
            test_data.iloc[ i + 3 ]["bikes_available"] = ev_bikes
            test_data.iloc[ i + 3 ]["slots_available"] = ev_slots
            true_bikes = true_test_data.iloc[ i + 3 ]["bikes_available"]
            mse = pow((ev_bikes-true_bikes), 2)
            print "%d,%f,%d,%f" % (i, ev_bikes, true_bikes, mse)
            

# <codecell>
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
        dc_station_17_poisson = pd.DataFrame.from_records(station_data, columns = ["station_id", "bikes_available", "spaces_available", "timestamp"], index = "timestamp")
        dc_station_17_poisson.index = dc_station_17_poisson.index.tz_localize('UTC').tz_convert('US/Eastern')

        print >> sys.stderr, "Running model validation script for poisson."
        model_validation(poisson_fit, 25, dc_station_17_poisson, station_id, start_date)

# <codecell>
    elif model == "binomial":

        from fetch_station import fetch_station
        dc_station_17_binomial = fetch_station("Washington, D.C.", station_id, 15, 'max')

        print >> sys.stderr, "Running model validation script for binomial."
        model_validation(binomial_fit, 25, dc_station_17_binomial, station_id, start_date)

    else:
        print >> sys.stderr, "Can't validate that model!"

