# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

import numpy as np
import statsmodels.api as sm
from scipy import stats
from matplotlib import pyplot as plt

import os
import psycopg2
import pandas as pd


# Fetch all records for a single station (tfl_id == 5)
conn = psycopg2.connect("dbname="+os.environ.get('dbname')+" user="+os.environ.get('dbuser')+ " host="+os.environ.get('dburl'))

cur = conn.cursor()

# Executes a SQL command
# This SQL command selects all rows from the boston database where the station ID is 5
cur.execute("SELECT * FROM bike_ind_boston WHERE tfl_id = 5;")

# Fetches all rows in the table output of the SQL query. 
# Remember to assign to a variable because we can only use fetchall() once for each SQL query.
boston_5 = cur.fetchall()

# Note that we cannot directly print boston_5. In order to view portions of it, we can use boston_5.head() [see below]

# <codecell>

# Converts python list of tuples containing data to a pandas dataframe, and renames the columns.
# 
# Set timezone
timezone = 'US/Eastern'

# Import data and set index to be timestamp
boston_5_df = pd.DataFrame.from_records(boston_5, columns = ["station_id", "bikes_available", "slots_available", "timestamp"], index = ["timestamp"])

boston_5_df.index = boston_5_df.index.tz_localize('UTC').tz_convert(timezone)

#put all data into 15 minute buckets, since some data was collected every 2 minutes and some every minute
boston_5_bucketed = boston_5_df.resample('2MIN')

# Drop rows that have missing observations for bikes_available or slots_available
boston_5_bucketed = boston_5_bucketed[np.isfinite(boston_5_bucketed['bikes_available'])]
boston_5_bucketed = boston_5_bucketed[np.isfinite(boston_5_bucketed['slots_available'])]

# <codecell>

# Calculate the percent full 
#first convert to arrays so that Python doesn't do integer division
bikes_available=np.asarray(boston_5_bucketed["bikes_available"], dtype=np.float32)
print bikes_available[0:50]
print np.isnan(np.min(bikes_available))
slots_available=np.asarray(boston_5_bucketed["slots_available"], dtype=np.float32)
print slots_available[0:50]

# Fix for Convergence Issues Using MLE, Option 1: Zero Entries -> 0.01 or Option 2: All Entries += 0.01 (Similar Results)
bikes_available[bikes_available == 0] = 0.01
slots_available[slots_available == 0] = 0.01

#bikes_available = bikes_available+0.01
#slots_available = slots_available+0.01

# Creating list of [success , failure] outcomes
bikes_slots_available=np.asarray(zip(bikes_available,slots_available))

# Creating Lags of Bike and Slot Variables
bikes_available_lag0 = bikes_available[1:]
bikes_available_lag1 = bikes_available[0:len(bikes_available)-1]
slots_available_lag1 = slots_available[0:len(slots_available)-1]
bikes_slots_available = bikes_slots_available[1:]

# Calculated the lag-log-odds ratio 
phat_lag1 = (bikes_available_lag1) / (bikes_available_lag1+slots_available_lag1)

logodds_lag1 = np.log( phat_lag1 / (1-phat_lag1) )


# Add Constant to Exogenous Variables
logodds_lag1 = sm.add_constant(logodds_lag1, prepend=False)


# Fit Binomial Regression.  Coefficients constant in time

glm_binom = sm.GLM(bikes_slots_available, logodds_lag1, family=sm.families.Binomial())

res = glm_binom.fit()

print res.summary()

# <codecell>

# This model includes month effects and one previous time point
##### previous time point is very significant predictor; months are not

import datetime
import patsy
from patsy.contrasts import Treatment

# Set up data frame with one lagged time point and a constant
data = pd.DataFrame(logodds_lag1, columns = ["logodds", "constant"])

# Strip month information from original timestamp variable
month = pd.DatetimeIndex(boston_5_bucketed.index).month

# Month as a factor variable
# Method 1 - doesn't work
# Month =pd.Factor(month[1:]-1, ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])

# Method 2- doesn't work
#month = pd.Categorical.from_array(month[1:])
#print patsy.dmatrix('month')

#method 3
levels = [3,4,5,6,7,8,9,10,11,12]
contrast = Treatment(reference=0).code_without_intercept(levels)
print contrast.matrix
month_dummy = contrast.matrix[month-3, :]

#drop first row because of lagged variable
month_dummy = month_dummy[1:, :]

#feel free to try to make this work... bree ran out of patience and did it the ugly way below
#month_dummy.dtype.names = ('Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec')
#data['Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'] = month_dummy[:,0:11]

#add dummy variables to dataset, using March as a reference variable.  do not add Jan or Feb because there are no observations in these months
data['jul'] = month_dummy[:,3]
data['aug'] = month_dummy[:,4]
data['sep'] = month_dummy[:,5]
data['oct'] = month_dummy[:,6]
data['nov'] = month_dummy[:,7]
data['dec'] = month_dummy[:,8]
data['apr'] = month_dummy[:,0]
data['may'] = month_dummy[:,1]
data['jun'] = month_dummy[:,2]

print data[1:10]
#run model
glm_binom_2 = sm.GLM(bikes_slots_available, data, family=sm.families.Binomial())

res = glm_binom_2.fit()

print res.summary()

# <codecell>


# Extract time of day from original data in 1 hour buckets
time_of_day = pd.DatetimeIndex(boston_5_bucketed.index).hour
#logodds_lag_data.head()

levels = list(range(0,24))
contrast = Treatment(reference=0).code_without_intercept(levels)
#print contrast.matrix
time_dummy = contrast.matrix[time_of_day, :]
time_dummy = time_dummy[1:, :]

# Midnight is reference variable

data['1AM'] = time_dummy[:,0]
data['2AM'] = time_dummy[:,1]
data['3AM'] = time_dummy[:,2]
data['4AM'] = time_dummy[:,3]
data['5AM'] = time_dummy[:,4]
data['6AM'] = time_dummy[:,5]
data['7AM'] = time_dummy[:,6]
data['8AM'] = time_dummy[:,7]
data['9AM'] = time_dummy[:,8]
data['10AM'] = time_dummy[:,9]
data['11AM'] = time_dummy[:,10]
data['12PM'] = time_dummy[:,11]
data['1PM'] = time_dummy[:,12]
data['2PM'] = time_dummy[:,13]
data['3PM'] = time_dummy[:,14]
data['4PM'] = time_dummy[:,15]
data['5PM'] = time_dummy[:,16]
data['6PM'] = time_dummy[:,17]
data['7PM'] = time_dummy[:,18]
data['8PM'] = time_dummy[:,19]
data['9PM'] = time_dummy[:,20]
data['10PM'] = time_dummy[:,21]
data['11PM'] = time_dummy[:,22]


glm_binom_3 = sm.GLM(bikes_slots_available, data, family=sm.families.Binomial())

res = glm_binom_3.fit()

print res.summary()

# <codecell>

#model with seasonal effects instead of monthly effects
#not working yet

#reset data so that it does not include month
#data = pd.DataFrame(logodds_lag1, columns = ["logodds", "constant"])
season = []
#create seasonal indicator variable
for i in range(0,len(month)):
    #print i
    if month[i]==0 | month[i] == 1 | month[i]==11 :
        try:
            season.append("winter")
        except:
            print i
            break
    elif month[i]==2| month[i] == 3 | month[i] == 4:
        try:
            season.append("spring")
        except:
            print i
            break
    elif month[i]==5| month[i] == 6 | month[i] == 7:
        try:
            season.append("summer")
        except:
            print ":(" +str(i)
            break
    elif month[i]==8| month[i] == 9 | month[i] == 10:
        try:
            season.append("spring")
        except:
            print i
            break

#make dummy variables for season

levels = [1,2,3,4]
contrast = Treatment(reference=0).code_without_intercept(levels)
print contrast.matrix
season_dummy = contrast.matrix[season-1, :]

#drop first row because of lagged variable
month_dummy = month_dummy[1:, :]

# <codecell>

#goal: calculate the monthly average number of bikes

month_series= pd.Series(month)

month_series.value_counts()

# <codecell>

print data.shape
print type(phat_lag1)

# <codecell>


