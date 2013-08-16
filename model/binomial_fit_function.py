def binomial_fit(data,stationid,n):
    import patsy
    import statsmodels.api as sm
    from scipy import misc
    import numpy as np
    import pandas as pd
    
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
    results = model.fit()

    def output(test_data, n):
        # Make lag dataframe
        #test_data_orig, no_one_cares_about_this = build_log_odds_df(test_data)
        #print "original test data"
        #print test_data_orig
        #print "present test data"
        bikes_available=np.asarray(test_data["bikes_available"], dtype=np.float32)
        slots_available=np.asarray(test_data["slots_available"], dtype=np.float32)

        phat = bikes_available / (bikes_available + slots_available)
        logodds = np.log(phat/(1-phat))
        df = pd.DataFrame(logodds)
        df = df.transpose()
        df['timestamp'] = data.index[2]
        df = pd.DataFrame.from_records(df, index = "timestamp")
        new_data = data.copy()
        new_data.ix[2,0] = logodds[2]
        new_data.ix[2,1] = logodds[1]
        new_data.ix[2,2] = logodds[0]
        column_list = ["logodds_lag1", "logodds_lag2", "logodds_lag3"]
        old_list = list(new_data.columns)
        new_data.columns = column_list + old_list[3:]
        new_data['const'] = [1]*len(new_data)
        
        #print test_data_log
        
        X_columns = ["temperature", "logodds_lag1", "logodds_lag2", "logodds_lag3", "const"] 
        X = new_data.ix[:, X_columns]
        
        # Extract time features
        test_log_hour_df = make_dummy(X, "hour")
        test_X = make_dummy(test_log_hour_df, "weekday")
        test_X = test_X.iloc[2]
        #print test_X
        # build design matrix
        p = results.predict(test_X)
        #print "p"
        pred_prob = [misc.comb(n,k, exact = 1)* (p ** k) * ((1-p) ** (n-k)) for k in range(0, n+1)]
        ev_bikes = n*p
        return pred_prob,ev_bikes
    
    return output
