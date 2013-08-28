# Poisson Arrival and Departure Models

We model passenger arrival at stops via [Negative Binomial Regression](http://ehs.sph.berkeley.edu/hubbard/longdata/webfiles/poissonmarch2005.pdf)

### File Descriptions

1. [poisson_data_extract.py](./poisson_data_extract.py) : Python script which contains all the data munging subscripts
  * Functions : Currently all functions are specific to Washington DC
    * <code> get_station_data() </code> : Retrieves all data bike availability data pertaining to a particular station
    * <code> calc_non_rebalance_change() </code>: Extracts rebalancing information for a given station
    * <code> rebalance_station_poisson_data() </code>: Produces a timeseries indexed dataframe that contains:
      * arrivals -> the number of arrivals per time interval (eg '1H')
      * departures -> the number of departures per time interval
      * months -> an indicator of the month which
      * hours ->
      * weekday_dummy ->
2. [poisson_fit.py](./poisson_fit.py) : Python Script which contains all the fit and prediction subscripts
  * Functions : Currently all functions are specific to Washington DC
    * <code> fit_poisson() </code>:  Takes station_id,  
