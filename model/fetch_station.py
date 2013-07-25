# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

def fetch_station(city, station_id, time_agg_level):
    import os
    import psycopg2
    import pandas as pd
    import numpy as np
    
    # Dictionary of timezones
    timezones = {'Chicago':'US/Central','Boston':'US/Eastern','New York':'US/Eastern','Washington, D.C.':'US/Eastern'}
    
    # Connect to the database
    conn = psycopg2.connect("dbname="+os.environ.get('dbname')+" user="+os.environ.get('dbuser')+ " host="+os.environ.get('dburl'))

    cur = conn.cursor()
    
    # Set timezone
    timezone = timezones[city]
        
    if city == "Washington, D.C.":
        city = "washingtondc"
        
    lower_city = city.lower()

    # Executes a SQL command
    # This SQL command selects all rows from the boston database where the station ID is 5
    cur.execute("SELECT * FROM bike_ind_"+str(lower_city)+" WHERE tfl_id = "+str(station_id)+";")

    # Fetches all rows in the table output of the SQL query. 
    # Remember to assign to a variable because we can only use fetchall() once for each SQL query.
    station = cur.fetchall()
    
    # Converts python list of tuples containing data to a pandas dataframe, and renames the columns.

    # Import data and set index to be timestamp
    station_df = pd.DataFrame.from_records(station, columns = ["station_id", "bikes_available", "slots_available", "timestamp"], index = ["timestamp"])

    station_df.index = station_df.index.tz_localize('UTC').tz_convert(timezone)

    #put all data into 15 minute buckets, since some data was collected every 2 minutes and some every minute
    station_bucketed = station_df.resample(str(time_agg_level)+'MIN')

    # Drop rows that have missing observations for bikes_available or slots_available
    station_bucketed = station_bucketed[np.isfinite(station_bucketed['bikes_available'])]
    station_bucketed = station_bucketed[np.isfinite(station_bucketed['slots_available'])]
    return station_bucketed

# <codecell>

# Test
#boston_5 = fetch_station('Boston',5,15)
#dc_5 = fetch_station("Washington, D.C.",5,15)

# <codecell>

#boston_5.head()

# <codecell>

#

