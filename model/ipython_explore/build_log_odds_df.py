# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

def build_log_odds_df(data):
    import pandas as pd
    from change_mat_binom import change_mat_binom
    import numpy as np
    import statsmodels.api as sm
    from scipy import stats
    from matplotlib import pyplot as plt
    from make_dummy import make_dummy
    
    # Calculate the percent full 
    #first convert to arrays so that Python doesn't do integer division
    bikes_available=np.asarray(data["bikes_available"], dtype=np.float32)
    slots_available=np.asarray(data["slots_available"], dtype=np.float32)
    
    # Fix for Convergence Issues Using MLE, Option 1: Zero Entries -> 0.01 or Option 2: All Entries += 0.01 (Similar Results)
    bikes_available[bikes_available == 0] = 0.0001
    slots_available[slots_available == 0] = 0.0001
    
    # Creating list of [success , failure] outcomes
    bikes_slots_available=np.asarray(zip(bikes_available,slots_available))
    
    # create log odds ratio of bikes to slots
    phat = bikes_available / (bikes_available + slots_available) 
    logodds = np.log(phat/(1-phat))
    
    logodds_lag3, outcome_ar3 = change_mat_binom(logodds, bikes_slots_available, 3)
    logodds_lag3_df = pd.DataFrame(logodds_lag3, columns = ["logodds_lag1", "logodds_lag2", "logodds_lag3"])
    
    # set the index in logodds_lag3 to match the time index in data
    lagged_data = data.ix[3:,:]
    logodds_lag3_df.index = lagged_data.index
    
    # add new lagged logodds to nonlagged predictor variable temperature
    pred_ar3_basic = logodds_lag3_df
    pred_ar3_basic["temperature"] = data.ix[3:,"temperature"]
        
    # add dummy variables for parts of time to design matrix
    X_with_hour = make_dummy(pred_ar3_basic, "hour")
    X = make_dummy(X_with_hour, "weekday")
    data = X
    
    # multiply the lagged logodds by hour bucket indicators
    
    # recode all_time_dummy to be 1 if the observations between midnight and 1 a.m. (this happens when all other columns of all_time_dummy sum to 0)
    
    zeros_series = pd.Series(np.zeros([len(X.index)]), index = X.index)
    print zeros_series.shape
        
    all_time_dummy = X.ix[:,"1hr":"23hr"]
    all_time_dummy["0hr"] = zeros_series
    for i in range(len(all_time_dummy.index)):
        if np.sum(all_time_dummy.ix[i,:]) == 0:
            all_time_dummy.ix[i,23] = 1

    # create matrix of zeros and ones to indicate which time period a point falls into

    n_time_buckets = 3
    step1 = np.zeros((all_time_dummy.shape[0], n_time_buckets))
    for i in range(0, 24, 24/n_time_buckets):
        for j in range(len(all_time_dummy.index)):
            step1[j,i/(24/n_time_buckets)] = np.sum(all_time_dummy.ix[j,i: i + 24/n_time_buckets], axis = 1)


    # multiply predictor variable by each column of created 0/1 matrix
    # want to do this for each lagged time variable- start with only one previous time point
    for j in range(3):
        for i in range(0, n_time_buckets):
            next_col = pd.DataFrame(step1[:,i]*logodds_lag3[:,j], columns = ["logodds_lag_" + str(j + 1) + "_time_bucket_" + str(i + 1)], index = X.index)
            data = pd.concat((data, next_col), axis = 1)


    # remove original lagged variable, add new versions that are multiplied by time of day indicator
    colnames = set(data.columns)
    for i in range(1,4):
        colnames.remove("logodds_lag" + str(i))

    data_no_cons = data.ix[:, colnames]
    
    # Add Constant to Exogenous Variables
    data_final = sm.add_constant(data_no_cons, prepend=False)
    return data_final, bikes_slots_available

# <codecell>

def make_present_logodds_df(test_endog):
    import numpy as np
    
    # remove logodds_lag3
    colnames = set(test_endog.columns)
    #colnames.remove("logodds_lag3")
    
    test_endog_no_lag3 = test_endog.ix[:, colnames]
    
    # create logodds_lag0
    # Calculate the percent full 
    #first convert to arrays so that Python doesn't do integer division
    bikes_available=np.asarray(test_endog_no_lag3["bikes_available"], dtype=np.float32)
    slots_available=np.asarray(test_endog_no_lag3["slots_available"], dtype=np.float32)
    
    # create log odds ratio of bikes to slots
    phat = bikes_available / (bikes_available + slots_available) 
    logodds = np.log(phat/(1-phat))
    
    test_endog_no_lag3["logodds_lag0"] = logodds
    return test_endog_no_lag3

# <codecell>


# <codecell>


# <codecell>


# <codecell>


# <codecell>


# <codecell>


# <codecell>


# <codecell>


# <codecell>


# <codecell>


