# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

import numpy as np
import statsmodels.api as sm
from scipy import stats
from matplotlib import pyplot as plt
import sklearn

import os
import psycopg2
import pandas as pd
from fetch_station import fetch_station

# Fetch all records for a single station (tfl_id == 5)
boston_5_bucketed = fetch_station('Boston',5,15, 'max')

# <codecell>

# Calculate the percent full 
#first convert to arrays so that Python doesn't do integer division
bikes_available=np.asarray(boston_5_bucketed["bikes_available"], dtype=np.float32)
slots_available=np.asarray(boston_5_bucketed["slots_available"], dtype=np.float32)

# Fix for Convergence Issues Using MLE, Option 1: Zero Entries -> 0.01 or Option 2: All Entries += 0.01 (Similar Results)
bikes_available[bikes_available == 0] = 0.01
slots_available[slots_available == 0] = 0.01

#bikes_available = bikes_available+0.01
#slots_available = slots_available+0.01

# Creating list of [success , failure] outcomes
bikes_slots_available=np.asarray(zip(bikes_available,slots_available))

# create log odds ratio of bikes to slots
phat = bikes_available / (bikes_available + slots_available) 
logodds = np.log(phat/(1-phat))

# Creating Lags of Bike and Slot Variables
bikes_available_lag0 = bikes_available[1:]
bikes_available_lag1 = bikes_available[0:len(bikes_available)-1]
slots_available_lag1 = slots_available[0:len(slots_available)-1]
bikes_slots_available_lag1 = bikes_slots_available[1:]

# Calculated the lag-log-odds ratio 
phat_lag1 = (bikes_available_lag1) / (bikes_available_lag1+slots_available_lag1)
#print "phat_lag1" + str(phat_lag1)
#print len(phat_lag1)

logodds_lag1 = np.log( phat_lag1 / (1-phat_lag1) )


# Add Constant to Exogenous Variables
logodds_lag1_cons = sm.add_constant(logodds_lag1, prepend=False)


# Fit Binomial Regression.  Coefficients constant in time

glm_binom = sm.GLM(bikes_slots_available_lag1, logodds_lag1_cons, family=sm.families.Binomial())

res = glm_binom.fit()

print res.summary()

# <codecell>

# This model includes month effects and one previous time point
##### previous time point is very significant predictor; months are not

import datetime
import patsy
from patsy.contrasts import Treatment

# Set up data frame with one lagged time point and a constant
data = pd.DataFrame(logodds_lag1_cons, columns = ["logodds", "constant"])

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
glm_binom_2 = sm.GLM(bikes_slots_available_lag1, data, family=sm.families.Binomial())

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


glm_binom_3 = sm.GLM(bikes_slots_available_lag1, data, family=sm.families.Binomial())

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
    # winter
    if month[i]==0 | month[i] == 1 | month[i]==11 :
        try:
            season.append(0)
        except:
            print i
            break
    # spring
    elif month[i]==2 | month[i] == 3 | month[i] == 4:
        try:
            season.append(1)
        except:
            print i
            break
    # summer
    elif month[i]==5 | month[i] == 6 | month[i] == 7:
        try:
            season.append(2)
        except:
            print ":(" +str(i)
            break
    # fall
    elif month[i]==8 | month[i] == 9 | month[i] == 10:
        try:
            season.append(3)
        except:
            print i
            break

#make dummy variables for season

levels = [0,1,2,3]
contrast = Treatment(reference=0).code_without_intercept(levels)
#print contrast.matrix
season_df = pd.DataFrame(season)
season_dummy = contrast.matrix[season_df-1, :]

#drop first row because of lagged variable
month_dummy = month_dummy[1:, :]

# <codecell>

# incorporate day of week
day_of_week = pd.DatetimeIndex(boston_5_bucketed.index).weekday

levels = list(range(0,7))
contrast = Treatment(reference=0).code_without_intercept(levels)

day_dummy = contrast.matrix[day_of_week, :]
day_dummy = day_dummy[1:, :]

# Monday is the reference variable
data['TUES'] = time_dummy[:,0]
data['WED'] = time_dummy[:,1]
data['THUR'] = time_dummy[:,2]
data['FRI'] = time_dummy[:,3]
data['SAT'] = time_dummy[:,4]
data['SUN'] = time_dummy[:,5]

data.ix[0,:]



# <codecell>

#goal: calculate the monthly average number of bikes

month_series= pd.Series(month)

month_series.value_counts()

# <codecell>

# AR(3) model

# function from energy team to create matrix of predictors
def change_mat(ts, binom, d):
    """Recieve a time series and a markov delay period.
       Return a matix of that design."""
    n=len(ts)
    x = np.array(ts[(d-1):n-1])
    for r in range(2,d+1):
        b = np.array(ts[(d-r):(n-r)])
        x = np.concatenate([x.reshape(len(x),-1),b.reshape(len(b),-1)],axis=1)
    y = binom[d:]
    return x, y

pred_ar3, outcome_ar3 = change_mat(logodds, bikes_slots_available, 3)

glm_ar3 = sm.GLM(outcome_ar3, pred_ar3, family=sm.families.Binomial())

results = glm_ar3.fit()

print results.summary()

# <codecell>

# vary coefficients based on time of day
# start with a model that has two sets of coefficients per day- one for midnight to noon, one for noon to midnight
all_time_dummy = numpy.append(time_dummy,numpy.zeros([len(time_dummy),1]),1)

# recode all_time_dummy to be 1 if the observations between midnight and 1 a.m. (this happens when all other columns of all_time_dummy sum to 0)
for i in range(len(all_time_dummy[:,0])):
    if np.sum(all_time_dummy[i,:]) == 0:
        all_time_dummy[i,23] = 1

# create matrix of zeros and ones to indicate which time period a point falls into
morning = np.sum(all_time_dummy[:,0:8], axis=1)
midday = np.sum(all_time_dummy[:,8:16], axis=1)
evening = np.sum(all_time_dummy[:,16:23], axis=1)

print morning[1:10]

#for i in range(len(morning)):
 #   if (morning[i] == 0 and midday[i] == 0 and evening[i] == 0):
  #      evening[i] = 1



# multiply predictor variable by each column of created 0/1 matrix
# want to do this for each lagged time variable- start with only one previous time point
morn_logodds = pd.DataFrame(morning * logodds_lag1, columns = ["I_morn"])
print morn_logodds.head()
mid_logodds = pd.DataFrame(midday * logodds_lag1, columns= ["I_mid"])
eve_logodds = pd.DataFrame(evening * logodds_lag1, columns = ["I_eve"])

# remove original lagged variable, add new versions that are multiplied by time of day indicator
colnames = set(data.columns)
colnames.remove("logodds")

ar1_pred = data.ix[:, colnames]
ar1_pred = pd.concat([ar1_pred, morn_logodds, mid_logodds, eve_logodds], axis=1)

        
# fit model
glm_ar1_timevary = sm.GLM(bikes_slots_available_lag1, ar1_pred, family=sm.families.Binomial())

results = glm_ar1_timevary.fit()

print results.summary()

# use result as predictor in model

# <codecell>

#pickling to send stuff to Scott

import cPickle
cPickle.dump(phat_lag1, open("phatlag1.pkl", "wb"))

boston_5_bucketed_lag = boston_5_bucketed.ix[1:,:]
timestamps_lag1 = pd.DatetimeIndex(boston_5_bucketed_lag.index)
cPickle.dump(timestamps_lag1, open("timestampslag1.pkl", "wb"))

# <codecell>

sum(ar1_pred.ix[:,"morn_logodds"], axis=1)

# <codecell>

x= np.asarray([1,2,3,4])
y = np.asarray([1,2,3,4])
x*y

# <codecell>

np.sum(time_dummy[:,0:12], axis=1))

# <codecell>

type(time_dummy)

# <codecell>

time_dummy[:,0:12]

# <codecell>

ar1_pred.ix[:,"morn_logodds"]

# <codecell>

data.ix[:,data.columns - data["logodds"]]

# <codecell>

data.columns.remove("logodds")

# <codecell>

colnames = set(data.columns)
colnames.remove("logodds")
colnames

# <codecell>

time_dummy[:,23] = 0

# <codecell>

type(time_dummy)

# <codecell>


# <codecell>

len(all_time_dummy[0,:])

# <codecell>

print len(logodds_lag1)
print logodds_lag1.shape

# <codecell>

print len(morning)

# <codecell>

print len(midday)
print morning.shape

# <codecell>

print len(evening)

# <codecell>

a = np.asarray([[1,2,4,5],[2,2,2,2]])
b = np.asarray([2,3,5,6])
a*b

# <codecell>


# <codecell>

a*b

# <codecell>


