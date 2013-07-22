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

# Converts python list of tuples containing data to a pandas dataframe, and renames the columns.
# 
# Set timezone
timezone = 'US/Eastern'

# Import data and set index to be timestamp
boston_5_df = pd.DataFrame.from_records(boston_5, columns = ["station_id", "bikes_available", "slots_available", "timestamp"], index = ["timestamp"])

boston_5_df.index = boston_5_df.index.tz_localize('UTC').tz_convert(timezone)

#put all data into 15 minute buckets, since some data was collected every 2 minutes and some every minute
boston_5_bucketed = boston_5_df.resample('15MIN')

# Drop rows that have missing observations for bikes_available or slots_available
boston_5_bucketed = boston_5_bucketed[np.isfinite(boston_5_bucketed['bikes_available'])]
boston_5_bucketed = boston_5_bucketed[np.isfinite(boston_5_bucketed['slots_available'])]

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
bikes_slots_available=numpy.asarray(zip(bikes_available,slots_available))

# Creating Lags of Bike and Slot Variables
bikes_available_lag0 = bikes_available[1:]
bikes_available_lag1 = bikes_available[0:len(bikes_available)-1]
slots_available_lag1 = slots_available[0:len(slots_available)-1]
bikes_slots_available = bikes_slots_available[1:]

# Calculated the lag-log-odds ratio 
phat_lag1 = (bikes_available_lag1) / (bikes_available_lag1+slots_available_lag1)

logodds_lag1 = log( phat_lag1 / (1-phat_lag1) )

# Add Constant to Exogenous Variables
logodds_lag1 = sm.add_constant(logodds_lag1, prepend=False)


# Fit Binomial Regression.  Coefficients constant in time

glm_binom = sm.GLM(bikes_slots_available, logodds_lag1, family=sm.families.Binomial())

res = glm_binom.fit()

print res.summary()

# <codecell>

#fit model with first 100 time points, predict next 5

glm_binom = sm.GLM(bikes_slots_available[0:100], logodds_lag1[0:100], family=sm.families.Binomial())

res = glm_binom.fit()

print res.summary()

x_new = logodds_lag1[100:105]

y_pred = res.predict(x_new)

#y_pred is on log odds scale
#print y_pred
n_slots = 15

#convert y_pred scale to number of bikes
pred_bikes_available = n_slots*(e**y_pred/(1+ e**y_pred))
print pred_bikes_available

print bikes_available[100:105]

# <codecell>

#goal: put previous cell inside for loop

#test by starting with 1000 rows of data

#will build a model contianing min_points first, then min_points + train_shift, min_points + 2* train_shift, etc.

# min_points is the minimum number of data points with which to fit a model.  The first model will be fit with the first min_points data points
min_points = 500

# train_shift is the number of data points to add to the training data set with each subsequent time the model is fit
train_shift = 100

# n_slots is the number of slots available for bikes at the station we are modeling
n_slots = 15

# n_forecast is the number of predictions to make past the last time point that is included in training data
n_forecast = 5

# n_iter is the number of validation models to fit
# fix n_iter for now, later use min_points, train_shift and size of data frame to calculate
n_iter = 5
# n_iter = np.floor((len(y) - min_points - n_forecast) / train_shift) + 1 
# This is what n_iter will be when we want to use the full dataset

# y_train is the outcome variable for the model
# because the model being fit is Binomial, y_train is an n by 2 array of [number of bikes available, number of slots available]
y_train = bikes_slots_available
# x_train is the array of predictor variables for the model
x_train = logodds_lag1

# set up empty MSE list to hold MSE
MSE = []
plots = []

for i in range(n_iter):
    glm_binom = sm.GLM(y_train[0: (min_points + i*train_shift)], x_train[0: (min_points + i*train_shift)], family=sm.families.Binomial())
    
    results = glm_binom.fit()
    
    p_hat = []
    
    predictor = x_train[(min_points + i*train_shift)]
    
    Y_hat = results.predict(predictor)
    
    p_hat.append(Y_hat)
    
    for n in range(1, n_forecast):
        # the input for .predict requires a constant, so use sm.add_constant
        # the caveat is that add_constant does not work with a one-dimensional array, so first make an array of Y_hat and .5 so that add_constant will work
        # since we only really care about Y_hat, not .5, only predict on the first row of the array
        predicted = results.predict(sm.add_constant(np.asarray([log(Y_hat/(1-Y_hat)), .5]), prepend=False)[0])
        
        # [Yhat, x_train[(min_points + i*train_shift),p:] ]
        # add predicted value to the array of previous predicted values
        p_hat.append(predicted)
        
        # update Y_hat to be predicted value from previous step
        Y_hat = predicted
    
    
    #convert y_pred scale to number of bikes
    pred_bikes_available = [n_slots*x for x in p_hat]
    
    # Error between prediction and actual
    this_test_MSE = (pred_bikes_available - y_train[(min_points + i*train_shift):(min_points + i*train_shift) + n_forecast,0])**2
    MSE.append(this_test_MSE)
    
    #figure(i)
    p, = plt.plot(np.asarray(range(1,len(MSE[i])+1)),MSE[i],label = "Test " + str(i))
    #legend([p], ["line " + str(i)])
    plots.append(p,)
    
    
    #print bikes_available[(min_points + i*train_shift) : (min_points + i*train_shift + n_forecast)]

print "MSE " + str(MSE)

for j in range(len(plots)):
    plots[j]
legend(plots)
plt.axis([1, n_forecast, 0, 20])
plt.title(r'Comparison of MSE of Different Test Runs')
plt.xlabel('Time Steps from Original Prediction')
plt.ylabel('Difference Between Predicted and Actual Number of Bikes at a Station')


#for t in range(n_forecast):
#    print "p%d = %s" % (t + 1, repr(MSE[t])), #= plot(x, MSE[t])

#print len(x)
#print MSE[0].shape
#p1, = plot(x, MSE[0])

# <codecell>

#goal: PLAY- Walter's cell

#test by starting with 1000 rows of data

#will build a model contianing min_points first, then min_points + train_shift, min_points + 2* train_shift, etc.

# min_points is the minimum number of data points with which to fit a model.  The first model will be fit with the first min_points data points
min_points = 500

# train_shift is the number of data points to add to the training data set with each subsequent time the model is fit
train_shift = 100

# n_slots is the number of slots available for bikes at the station we are modeling
n_slots = 15

# n_forecast is the number of predictions to make past the last time point that is included in training data
n_forecast = 10

# n_iter is the number of validation models to fit
# fix n_iter for now, later use min_points, train_shift and size of data frame to calculate
n_iter = 5
# n_iter = np.floor((len(y) - min_points - n_forecast) / train_shift) + 1 
# This is what n_iter will be when we want to use the full dataset

# y_train is the outcome variable for the model
# because the model being fit is Binomial, y_train is an n by 2 array of [number of bikes available, number of slots available]
y_train = bikes_slots_available
# x_train is the array of predictor variables for the model
x_train = logodds_lag1

glm_binom = sm.GLM(y_train, x_train, family=sm.families.Binomial())
    
results = glm_binom.fit()

pred_log_odds = []
    
predictor = x_train[24000]

predictor[0] = log((14./n_slots) / (1 - 14./n_slots))

Y_hat = results.predict(predictor)

print "First Predicted value " + str(Y_hat)
pred_log_odds.append(Y_hat)
    
for n in range(1, n_forecast):
    # the input for .predict requires a constant, so use sm.add_constant
    # the caveat is that add_constant does not work with a one-dimensional array, so first make an array of Y_hat and .5 so that add_constant will work
    # since we only really care about Y_hat, not .5, only predict on the first row of the array
    predicted = results.predict(sm.add_constant(np.asarray([log(Y_hat/(1-Y_hat)), .5]), prepend=False)[0])
        
    # add predicted value to the array of previous predicted values
    pred_log_odds.append(predicted)
        
    # update Y_hat to be predicted value from previous step
    Y_hat = predicted
    
    
print pred_log_odds
#convert y_pred scale to number of bikes
pred_bikes_available = [n_slots*x for x in pred_log_odds]
print "Predicted number of bikes, "
print pred_bikes_available
    
#print "Error between prediction and actual, " + i
    
#print bikes_available[(min_points + i*train_shift) : (min_points + i*train_shift + n_forecast)]

# <codecell>

print boston_5_bucketed[0:10]["bikes_available"]

# <codecell>

MSE[0]

# <codecell>

y_train[(min_points + i*train_shift)][0]

