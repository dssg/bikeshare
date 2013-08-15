# This function is used in the model validation script to predict bikes
def poisson_fit(data, stationid, n):
    import patsy
    import statsmodels.api as sm

    from pandas.io.parsers import read_csv
    from math import floor, exp

    from poisson_model import find_hourly_arr_dep_deltas, remove_rebalancing_deltas, fit_poisson, lambda_calc

    # Convert bike availability time series into hourly interval count data
    arrival_departure_deltas = find_hourly_arr_dep_deltas(data)

    # Remove hourly swings in bike arrivals and departures caused by station rebalancing
    rebalancing_data = '/mnt/data1/BikeShare/rebalancing_trips_2_2012_to_3_2013.csv'
    clean_arrival_departure_deltas = remove_rebalancing_deltas(arrival_departure_deltas, rebalancing_data, stationid)

    # Estimate the poisson point process
    print "Poisson results with rebalancing trips removed:"
    poisson_results = fit_poisson(clean_arrival_departure_deltas)

    def predict_bikes(test_data, n):
        "Compute the net lambda value - change in bikes at station - for a specific time interval (hour), month, and weekday."

        # Set prediction parameters
        current_bikes = test_data["bikes_available"][2]
        current_time = test_data.index[2]
        prediction_interval = .25
        month = current_time.month
        day_of_week = current_time.weekday
        if day_of_week < 5:
            weekday = 1
        else:
            weekday = 0

        # Create list of hour-chunks in between the current time and the prediction time
        # Need to do this to calculate cumulative lambda rate of arrivals and departures below.
        prediction_time = current_time + prediction_interval

        time_list = [current_time]
        next_step = current_time
        while next_step != prediction_time:
        
            if floor(next_step) + 1 < prediction_time:
                next_step = floor(next_step) + 1
            
            else:
                next_step = prediction_time
                
            time_list.append(next_step)
            
        # Calculate the cumulative lambda rate over the predition interval
        # For arrivals..
        arr_cum_lambda = 0 
        for i in range(1, len(time_list)):
            # Compute arrival lambda for entire current hour
            est_lambda = lambda_calc(month, time_list[ i - 1 ], weekday, poisson_results["arrivals"])

            # Find hour-chunk lambda
            hour_proportion = time_list[i] - time_list[ i - 1 ]
            interval_lambda = est_lambda * hour_proportion
            
            # Count up hour-chunk lambdas to get cumulative lambda
            arr_cum_lambda += interval_lambda
            
        # .. and departures
        dep_cum_lambda = 0 
        for i in range(1, len(time_list)):
            est_lambda = lambda_calc(month, time_list[ i - 1 ], weekday, poisson_results["departures"])
            hour_proportion = time_list[i] - time_list[ i - 1 ]
            interval_lambda = est_lambda * hour_proportion
            
            dep_cum_lambda += interval_lambda
        
        # Subtract cumulative departure lambdas from arrival lambdas to find net lamdas 
        # over the prediction interval
        net_lambda = arr_cum_lambda - dep_cum_lambda

        # Constrain number of bike predictions to max available bikes at station
        predicted_bikes = current_bikes + net_lambda
        if predicted_bikes > n:
            predicted_bikes = n
        elif predicted_bikes < 0:
            predicted_bikes = 0

        # Find probability distribution for bikes at stations given the current lambda
        probability_distribution = []

        prediction_output = (probability_distribution, predicted_bikes)
        
        return prediction_output

    return predict_bikes


