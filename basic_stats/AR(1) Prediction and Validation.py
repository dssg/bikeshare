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


# Fetch all records for a single station (tfl_id == 50)
conn = psycopg2.connect("dbname="+os.environ.get('dbname')+" user="+os.environ.get('dbuser')+ " host="+os.environ.get('dburl'))

cur = conn.cursor()

# Executes a SQL command
# This SQL command selects all rows from the boston database where the station ID is 5
cur.execute("SELECT * FROM bike_ind_boston WHERE tfl_id = 50;")

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
boston_5_bucketed = boston_5_df.resample('1MIN')

# Drop rows that have missing observations for bikes_available or slots_available
boston_5_bucketed = boston_5_bucketed[np.isfinite(boston_5_bucketed['bikes_available'])]
boston_5_bucketed = boston_5_bucketed[np.isfinite(boston_5_bucketed['slots_available'])]

# <codecell>

# Calculate the percent full 
#first convert to arrays so that Python doesn't do integer division
bikes_available=np.asarray(boston_5_bucketed["bikes_available"], dtype=np.float32) 
slots_available=np.asarray(boston_5_bucketed["slots_available"], dtype=np.float32)

# De-mean the process
mean_bikes_available = sum(bikes_available) / len(bikes_available)
bikes_available = bikes_available - mean_bikes_available


# Fix for Convergence Issues Using MLE, Option 1: Zero Entries -> 0.01 or Option 2: All Entries += 0.01 (Similar Results)
bikes_available[bikes_available == 0] = 0.01
slots_available[slots_available == 0] = 0.01

#bikes_available = bikes_available+0.01
#slots_available = slots_available+0.01

# Creating Lags of Bike and Slot Variables
bikes_available_lag0 = bikes_available[1:]
bikes_available_lag1 = bikes_available[0:len(bikes_available)-1]
slots_available_lag1 = slots_available[0:len(slots_available)-1]


# Fit Gaussian Regression.  Coefficients constant in time


results = [0]

for steps in range(1,6):
    MSE = 0
    for ref in range(1000,140000,100):
        y_lag0 = bikes_available_lag0[0:ref]
        y_lag1 = bikes_available_lag1[0:ref]
        # y_lag1 = sm.add_constant(y_lag1, prepend=False) 
    
        ARMA_1_0 = sm.GLM(y_lag0, y_lag1, family=sm.families.Gaussian())
        res = ARMA_1_0.fit()

        true_y = bikes_available_lag0[ref+steps]

        # pred_y = res.params[0] * bikes_available_lag1[ref+1] + res.params[1]
        pred_y = (res.params[0]**steps) * bikes_available_lag1[ref+1]

        MSE = MSE + (true_y - pred_y)**2

    MSE = MSE/len(range(1000,140000,100))

    results.append(MSE)

print results


# <codecell>

import matplotlib.pyplot as plt

plt.plot(results)

# <codecell>

resid = res.resid_deviance.copy()

sigmasq = sum(resid**2)/(ref-1)

# Predict Expected Value Sequence

def pred(alpha, step, y_lag0, avg): # Builds Prediction at Y_{t + step} for AR(1) process with coefficient alpha and mean avg
    result = [y_lag0]
    for i in range(1,step+1):
        pred = avg + (alpha**i) * (y_lag0 - avg)
        result.append(pred)
    return result


step = 60
y_lag0 = 10
mu1 = pred(res.params[0], step, y_lag0, mean_bikes_available)

sigma1 = [0]

for i in range(1,step+1):
    sigma1.append(sqrt(sigmasq*i))


# Plot the time against the number of bikes available, including the standard deviation

fig = plt.figure()
fig, ax = plt.subplots(1)

t = range(0,step+1)

mu1 = np.asarray(mu1) 
sigma1 = np.asarray(sigma1)

# print "mu1 is equal to "
# print mu1 - sigma1
# print "sigma1 is equal to "
# print sigma1

ax.plot(t, mu1, lw=2, label='mean population 1', color='red')
ax.plot(t, mu1)
ax.fill_between(t, (mu1-sigma1).tolist(), (mu1+sigma1).tolist(), facecolor='blue', alpha=0.5)
plt.show()
#boston_5_annual_averages.plot(x = 'timestamp', y = 'bikes_available')

# <codecell>

from scipy.stats import norm

# Find the Probability of 0 Bikes at Station 5 after _step_ minutes starting at y_lag0

def probzero(alpha, y_lag0, avg, sigmasq, step):
    mean = avg + (alpha **step) * (y_lag0 - avg)
    return norm.cdf(-mean / (sqrt(sigmasq*step)))

def probfull(alpha, y_lag0, avg, sigmasq, step, totalspots):
    mean = avg + (alpha **step) * (y_lag0 - avg)
    return 1 - norm.cdf((totalspots-mean) / (sqrt(sigmasq*step)))

x = probzero(res.params[0], 10, mean_bikes_available, sigmasq, 60)

x2 = probfull(res.params[0], 10, mean_bikes_available, sigmasq, 60, 15)

print x

print x2
    

# <codecell>


