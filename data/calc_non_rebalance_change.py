def calc_non_rebalance_change(station_number, time_interval):
    import pandas as pd
    from dateutil.parser import parse

    # read in rebalancing data
    rebalance = pd.io.parsers.read_csv("/mnt/data1/BikeShare/dc_rebalancing.csv", delimiter=",", parse_dates = [5])
    rebalance.columns = ['tech_num','start_station','start_terminal','end_station','end_terminal','start_date','end_date','last_technician_activity','duration','status_reason','bike_num']
    # Note: end_date has missing values, so it was not read in as a timestamp. 
    # This doesn't really matter right now, and we change it into a timestamp later once the missing values are dropped

    # read in crosswalk data
    xwalk = pd.io.parsers.read_csv("/mnt/data1/BikeShare/tfl_id_crosswalk.csv", delimiter = ",", names = ['start_tfl_id','start_terminal'])

    # merge on ids of start station
    rebalance_with_ids_start = pd.merge(rebalance, xwalk, on='start_terminal')

    start_deltas = rebalance_with_ids_start.ix[:,['start_tfl_id','start_date']]
    start_deltas.columns = ['tfl_id','timestamp']
    start_deltas['delta'] = 1
    start = start_deltas.set_index(start_deltas['timestamp'])

    # rename columns in order to merge on ids of end station
    xwalk.columns = ['end_tfl_id','end_terminal']

    # merge on ids of end station
    rebalance_with_ids_end = pd.merge(rebalance_with_ids_start, xwalk, on = 'end_terminal')
    end_deltas = rebalance_with_ids_end.ix[:,['end_tfl_id','end_date']]
    end_deltas.columns = ['tfl_id','timestamp']
    # change timestamp variable to be datetime type (there are no missing values now, so it converts easily)
    end_deltas['timestamp'] = pd.to_datetime(end_deltas['timestamp'])
    end_deltas['delta'] = -1
    end = end_deltas.set_index(end_deltas['timestamp'])

    # Concatenate dataframes with deltas
    deltas = pd.concat([start,end])
    
    # Extract a certain station
    deltas_station = deltas.ix[deltas['tfl_id'] == station_number,:]
    time_interval = time_interval
    agg = deltas_station['delta'].resample(time_interval, how ='sum')

    # Fill in missing values with zeroes 
    agg_no_NaNs = agg.fillna(0)
    return agg_no_NaNs