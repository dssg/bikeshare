# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

def binomial_fit(data, n, stationid):
    import patsy
    import statsmodels.api as sm
    from scipy import misc
    
    from build_log_odds_df import build_log_odds_df
    # Make lag dataframe
    pred_ar3_cons = build_log_odds_df(data)
    
    # Extract time features
    # Extract hours for Hour feature
    delta_hours = pred_ar3_cons.index.hour
    pred_ar3_cons['hours'] = delta_hours

    # Extract weekday vs. weekend variable
    delta_dayofweek = pred_ar3_cons.index.weekday

    delta_weekday_dummy = delta_dayofweek.copy()
    delta_weekday_dummy[delta_dayofweek < 5] = 1
    delta_weekday_dummy[delta_dayofweek >= 5] = 0

    pred_ar3_cons['weekday_dummy'] = delta_weekday_dummy
    
    # build design matrix
    y, X = patsy.dmatrices("log_bikes + log_slots ~ C(hours, Treatment) + C(weekday_dummy,Treatment) + temperature + logodds_lag1 + logodds_lag2 + logodds_lag3 ", pred_ar3_cons, return_type='dataframe')
    
    # fit the model!
    model = sm.GLM(y, X, family=sm.families.Binomial())
    results = model.fit()

    def output(test_data, n):
        # Make lag dataframe
        pred_ar3_cons = build_log_odds_df(test_data)
    
        # Extract time features
    
        # Extract hours for Hour feature
        delta_hours = pred_ar3_cons.index.hour
        pred_ar3_cons['hours'] = delta_hours

        # Extract weekday vs. weekend variable
        delta_dayofweek = pred_ar3_cons.index.weekday

        delta_weekday_dummy = delta_dayofweek.copy()
        delta_weekday_dummy[delta_dayofweek < 5] = 1
        delta_weekday_dummy[delta_dayofweek >= 5] = 0

        pred_ar3_cons['weekday_dummy'] = delta_weekday_dummy
    
    # build design matrix
        y, test_X = patsy.dmatrices("log_bikes + log_slots ~ C(hours, Treatment) + C(weekday_dummy,Treatment) + temperature + logodds_lag1 + logodds_lag2 + logodds_lag3 ", pred_ar3_cons, return_type='dataframe')
        p = results.predict(test_X)
        pred_prob = [misc.comb(n,k, exact = 1)* (p ** k) * ((1-p) ** (n-k)) for k in range(0, n+1)]
        ev_bikes = n*p
        return pred_prob,ev_bikes
    
    return output

