# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

import patsy
import statsmodels.api as sm
from scipy import misc
import numpy as np
import pandas as pd
import pickle
    
from build_log_odds_df import build_log_odds_df
from build_log_odds_df import make_present_logodds_df
from make_dummy import make_dummy_inner
from make_dummy import make_dummy
from fetch_station import fetch_station

# <codecell>

def binomial_save_parameters(data,n):
    import patsy
    import statsmodels.api as sm
    from scipy import misc
    import numpy as np
    
    from build_log_odds_df import build_log_odds_df
    from build_log_odds_df import make_present_logodds_df
    from make_dummy import make_dummy_inner
    from make_dummy import make_dummy
    
    # Make lag dataframe
    columns = ["bikes_available", "slots_available", "temperature"]
    data_trimmed = data.ix[:,columns]
    X_raw, y = build_log_odds_df(data_trimmed) 
    
    X_columns = ["temperature", "logodds_lag1", "logodds_lag2", "logodds_lag3", "const"] 
    X_no_outcome = X_raw.ix[:, X_columns]
    
    # build design matrix
    X_with_hour = make_dummy(X_no_outcome, "hour")
    X = make_dummy(X_with_hour, "weekday")
    
    #test_data = bike_data_bucketed.ix[100:104,:]
    #present_logodds_df = make_present_logodds_df(test_log_hour_weekday_df)
    # fit the model!
    model = sm.GLM(y, X, family=sm.families.Binomial())
    binomial_results = model.fit()
    return binomial_resutls
    
    

# <codecell>

dc_17=fetch_station("Washington, D.C.", 17, 15, 'max')

# <codecell>

station_ids = ['17']
city = "Washington, D.C."
def save_binomial_results():
    for station_id in station_ids:
        data = fetch_station(city, station_id, 15, 'max')
        binomial_results = binomial_save_parameters(data, station_id)
        file_out = open("/mnt/data1/BikeShare/pickles/binomial_results_%s.p" % station_id, "wb")
        pickle.dump(binomial_results, file_out)
        file_out.close()

# <codecell>

save_binomial_results()

# <codecell>


# <codecell>


# <codecell>


