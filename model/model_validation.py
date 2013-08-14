# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>


# <codecell>

import pandas as pd
from pandas.core.datetools import *
import numpy as np
from binomial_fit_function import binomial_fit

def model_validation(modelfit, n, data, startdate = None):
    if startdate == None:
        startdate = data.index[0]
    else:
        try:
            startdate = data[startdate:].index[0]
        except:
            print "That date is after the end of biketime. We'll choose the first date in our dataset."
            startdate = data.index[0]
            
    enddate = startdate + DateOffset(years=1)
    offset = DateOffset(days=1,hours=1)
    for i in range(10000):
        if i !=0:
            enddate += offset
            
        try:
            test_data = data[np.datetime64(enddate):].iloc[1:7]
            true_test_data = data[np.datetime64(enddate):].iloc[1:7]
        except:
            break
        else:
            print "Training on data up to %s" % str(enddate)
        
        fit_data = data[np.datetime64(startdate):np.datetime64(enddate)]
        model = modelfit(fit_data,n = None)
        print "Steps Out, Expected Number of Bikes,  True Expected Number of Bikes, MSE"
        for i in range(3):
            lst_prob,ev_bikes = model(test_data.iloc[i:(i+3)],n)
            ev_slots = n-ev_bikes
            test_data.iloc[i+3]["bikes_available"] = ev_bikes
            test_data.iloc[i+3]["slots_available"] = ev_slots
            true_bikes = true_test_data.iloc[i+3]["bikes_available"]
            mse = pow((ev_bikes-true_bikes),2)
            print "%d,%f,%d,%f" % (i,ev_bikes,true_bikes,mse)
            

# <codecell>

from fetch_station import fetch_station
dc_17=fetch_station("Washington, D.C.", 17, 15, 'max')

# <codecell>

#test_model = binomial_fit(dc_17,25)

# <codecell>

#test_model(dc_17,25)

# <codecell>

model_validation(binomial_fit,25,dc_17)

# <codecell>


# <codecell>


# <codecell>


