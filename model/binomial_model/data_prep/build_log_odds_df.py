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
    
    # Calculate the percent full 
    #first convert to arrays so that Python doesn't do integer division
    bikes_available=np.asarray(data["bikes_available"], dtype=np.float32)
    slots_available=np.asarray(data["slots_available"], dtype=np.float32)
    
    # Fix for Convergence Issues Using MLE, Option 1: Zero Entries -> 0.01 or Option 2: All Entries += 0.01 (Similar Results)
    bikes_available[bikes_available == 0] = 0.01
    slots_available[slots_available == 0] = 0.01
    
    # Creating list of [success , failure] outcomes
    bikes_slots_available=np.asarray(zip(bikes_available,slots_available))
    
    # create log odds ratio of bikes to slots
    phat = bikes_available / (bikes_available + slots_available) 
    logodds = np.log(phat/(1-phat))
    
    logodds_lag3, outcome_ar3 = change_mat_binom(logodds, bikes_slots_available, 3)
    logodds_lag3_df = pd.DataFrame(logodds_lag3, columns = ["logodds_lag1", "logodds_lag2", "logodds_lag3"])
    #outcome_ar3_df = pd.DataFrame(outcome_ar3, columns = ["log_bikes","log_slots"])
    
    # set the index in logodds_lag3 to match the time index in data
    lagged_data = data.ix[3:,:]
    logodds_lag3_df.index = lagged_data.index
    #outcome_ar3_df.index = lagged_data.index

    # add new lagged logodds to nonlagged predictor variables
    pred_ar3 = pd.concat([data.ix[3:,:], logodds_lag3_df], axis=1)
    #  pred_ar3 = pd.concat([data.ix[3:,:], logodds_lag3_df, outcome_ar3_df], axis=1)
    # Add Constant to Exogenous Variables
    pred_ar3_cons = sm.add_constant(pred_ar3, prepend=False)
    #return new_data
    return pred_ar3_cons, outcome_ar3

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


