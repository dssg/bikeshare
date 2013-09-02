# Poisson arrival and departure models

These scripts implement poisson model to predict the number of bikes at a bikeshare station. 

First the data is fetched, aggregated into hourly buckets, cleaned to remove rebalancing trips, and used to fit two poisson models - one for arrivals and one for departures - with time of day, month, weekday/weekend, hourly temperature, and hourly percipitation as covariates. Once the model has been learned, it can be used for prediction and simulation (as in the webapp,) and can be checked for predictive accuracy using out-of-sample rolling window validation. 

Check the [methodology section](https://github.com/dssg/bikeshare/wiki/methodology#poisson-point-process) of the wiki to read about how we're modeling bike station arrivals and departures as poisson point processes.

[poisson_data_extract.py](./poisson_data_extract.py) : Python script which contains all the data munging subscripts <br>
  * __Functions__ : Currently all functions are specific to Washington DC
     * <code> get\_station\_data() </code> : Retrieves all data bike availability data pertaining to a particular station
     * <code> calc_non_rebalance_change() </code>: Extracts rebalancing information for a given station
     * <code> rebalance_station_poisson_data() </code>: Produces a timeseries indexed dataframe that contains:
         * arrivals -> the number of arrivals per time interval (eg '1H')
         * departures -> the number of departures per time interval
         * months -> an indicator of the month in which the observation occurred
         * hours -> an indicator of the hour in which the observation occurred
         * weekday_dummy -> an indicator of whether the observation occurred during a weekday or weekend

[poisson_fit.py](./poisson_fit.py) : Python Script which contains all the fit and prediction subscripts

  * __Estimation Functions__ : Currently all functions are specific to Washington DC
     * <code> fit\_poisson() </code>:  Takes station\_id, start time, and end time and fits the poisson model for both departures and arrivals using data from that station during that time interval. 
         * Option included allows to user to indicate whether rebalancing should be included or not
     * <code> save\_poisson\_results() </code> : Runs the poisson fit code for a particular station and saves the results to a pickled file (ex _poisson\_results\_16\_rebalanced.p_)
     * <code> load\_poisson\_results() </code> : Loads the pickled poisson_results for a particular station
   
  * __Prediction Functions__ 
     * <code> predict\_net\_lambda </code> : Takes a current time, a prediction interval, and the results from <code> fit\_poisson() </code> to produce the expected value of change in bikes at some point in the future. Uses `lambda_calc` to caculate rate lambda of arrivals and departures over the interval, then finds the difference - the "net lambda" - to find expected value of change in bikes at the end of the interval. This is the core prediction function.
     * <code> lambda_calc </code> : Uses the fitted poisson models to calculate the appropriate rate parameter - of arrivals or departure, can be used for both - given month, time of day, and weekday indicators.
     * <code> simulation </code> : Uses the <code> simulate\_bikes </code> function to simulate the bike count trajectory over a given time interval, and repeats this a bunch of times (called trials). The function outputs three lists: (1) the number of bikes at the station at the final time for each trial (2) an indicator if the station ever went empty during the trail, and (3) an indicator if the station ever went full.
     * <code> simulate\_bikes </code> : Simulates bike counts from an initial to a final time for a particular station with a set number of docks and starting number of bikes. Call this function every time you want to simulate a dual poisson point process of simultaneous arrivals and departures. (Check the [methodology section](https://github.com/dssg/bikeshare/wiki/methodology#poisson-point-process) of the wiki to read about how we're simulating poisson point processes.)

[poisson_validation.py](./poisson_validation.py) : Python script that contains all functions related to validation of our current model
  * __Functions__ : Currently all functions are specific to Washington DC
     * <code>  fit\_poisson\_simulation </code> :  Produces the same estimation results as <code> fit\_poisson </code>, but it takes in the arrival and departure data directly.
     * <code> validation\_simulation </code> : Produces the same lists as <code> simulation </code> but takes in the poisson fitted results directly.
     * <code> arr\_and\_dep\_until\_time </code> : Extracts the observed arrivals and departures only up to a certain time.
     * <code> empty\_in\_window </code> :  Given a time window, checks the data to see if the station ever went empty in that window
     * <code> bikes\_at\_time </code> :  Given a time, finds the number of bikes at the station at this time.
     * <code> mse\_calculation </code> : Produces a MSE estimate given a minimum time point, a final time, an the time step in months, days, and hours.  Can be altered to provide alternative prediction metrics.
