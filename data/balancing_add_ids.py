import pandas as pd
from dateutil.parser import parse
import cPickle

rebalance = pd.io.parsers.read_csv("dc_rebalancing.csv", delimiter=",", parse_dates = [5])
rebalance.columns = ['tech_num','start_station','start_terminal','end_station','end_terminal','start_date','end_date','last_technician_activity','duration','status_reason','bike_num']

# end_date has missing values, so it was not read in as a timestamp
# change end_date into timesteamp
rebalance['end_date'] = pd.to_datetime(rebalance['end_date'],coerce=True)

xwalk = pd.io.parsers.read_csv("tfl_id_crosswalk.csv", delimiter = ",", names = ['start_tfl_id','start_terminal'])

# merge on ids of start station
rebalance_with_start_id = pd.merge(rebalance,xwalk,on='start_terminal')
# rename columns in order to merge on ids of end station
xwalk.columns = ['end_tfl_id','end_terminal']
# merge on ids of end station
rebalance_with_ids = pd.merge(rebalance_with_start_id, xwalk, how = 'outer')

start_deltas = rebalance_with_ids.ix[:,['start_tfl_id','start_date']]
start_deltas.columns = ['tfl_id','timestamp']
start_deltas['delta'] = 1
start = start_deltas.set_index(start_deltas['timestamp'])

end_deltas = rebalance_with_ids.ix[:,['end_tfl_id','end_date']]
end_deltas.columns = ['tfl_id','timestamp']
end_deltas['delta'] = -1
end = end_deltas.set_index(end_deltas['timestamp'])

# Concatenate
deltas = pd.concat([start,end])


#start = rebalance_with_ids.set_index(rebalance_with_ids['start_date'])
#end =  rebalance_with_ids.set_index(rebalance_with_ids['end_date'])
