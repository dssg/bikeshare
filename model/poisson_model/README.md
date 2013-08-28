# Poisson Arrival and Departure Models

### File Descriptions

1. [poisson_data_extract.py](./poisson_data_extract.py) : Python script which contains all the data munging subscripts <br>
__Functions__ : Currently all functions are specific to Washington DC
  * <code> get\_station\_data() </code> : Retrieves all data bike availability data pertaining to a particular station
  * <code> calc_non_rebalance_change() </code>: Extracts rebalancing information for a given station
  * <code> rebalance_station_poisson_data() </code>: Produces a timeseries indexed dataframe that contains:
     * arrivals -> the number of arrivals per time interval (eg '1H')
     * departures -> the number of departures per time interval
     * months -> an indicator of the month in which the observation occurred
     * hours -> an indicator of the hour in which the observation occurred
     * weekday_dummy -> an indicator of whether the observation occurred during a weekday or weekend

2. [poisson_fit.py](./poisson_fit.py) : Python Script which contains all the fit and prediction subscripts <br>
  * __Estimation Functions__ : Currently all functions are specific to Washington DC
     * <code> fit\_poisson() </code>:  Takes station\_id, start time, and end time and fits the poisson model for both departures and arrivals using data from that station during that time interval.  
         * Option included allows to user to indicate whether rebalancing should be included or not
     * <code> save\_poisson\_results() </code> : Runs the poisson fit code for a particular station and saves the results to a pickled file (ex _poisson\_results\_16\_rebalanced.p_)
     * <code> load\_poisson\_results() </code> : Loads the pickled poisson_results for a particular station
  * __Prediction Functions__ 
     * <code> lambda_calc </code> : Uses the fitted poisson models to calculate the appropriate rate parameter given month, time of day, and weekday indicators
     * <code> predict\_net\_lambda </code> : Takes a current time, a prediction interval, and the results from <code> fit\_poisson() </code> to produce the expected value of change in bikes at some point in the future
     * <code> simulate\_bikes </code> : Simulates a version of the bike counts from an initial to a final time for a particular station with a certain number of slots and starting number of bikes
     * <code> simulation </code> : Uses the <code> simulate\_bikes </code> function an simulates the bike count trajectory forward a certain number of trials.  Provides three lists (1) the number of bikes at the station at the final time for each trial (2) an indicator if the station every went empty (3) an indicator if the station ever went full.
