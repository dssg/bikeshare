# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

def fetch_station(city, station_id, time_agg_level,agg_type):
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
    #cur.execute("SELECT * FROM bike_ind_"+str(lower_city)+" WHERE tfl_id = "+str(station_id)+";")
    cur.execute("SELECT * FROM bike_ind_" +str(lower_city)+" INNER JOIN weather_"+str(lower_city)+" ON (date_part('year',bike_ind_"+str(lower_city)+".timestamp)=date_part('year',weather_"+str(lower_city)+".time) AND date_part('month',bike_ind_"+str(lower_city)+".timestamp)=date_part('month',weather_"+str(lower_city)+".time) AND date_part('day', bike_ind_"+str(lower_city)+".timestamp) = date_part('day', weather_"+str(lower_city)+".time) AND date_part('hour', bike_ind_"+str(lower_city)+".timestamp) = date_part('hour', weather_"+str(lower_city)+".time)) WHERE bike_ind_"+str(lower_city)+".tfl_id ="+str(station_id)+";")
    

    # Fetches all rows in the table output of the SQL query. 
    # Remember to assign to a variable because we can only use fetchall() once for each SQL query.
    station = cur.fetchall()
    
    # Converts python list of tuples containing data to a pandas dataframe, and renames the columns.

    # Import data and set index to be timestamp
    #station_df = pd.DataFrame.from_records(station, columns = ["station_id", "bikes_available", "slots_available", "timestamp"], index = ["timestamp"])
    station_df = pd.DataFrame.from_records(station, columns = ["station_id", "bikes_available", "slots_available", "bikes_timestamp", "weather_timestamp", "summary", "precipintensity", "precipprob", "preciptype", "precipaccumulation", "temperature"], index = ["bikes_timestamp"])

    station_df.index = station_df.index.tz_localize('UTC').tz_convert(timezone)
    
    # NOTE: The weather time stamp and station time stamp don't match, even after conversion...
    # Hunter looking into how weather data is collected in database
    station_df["weather_timestamp"] = station_df.ix[:,"weather_timestamp"].tz_convert(timezone)
    
    #station_df.index = station_df.index.tz_localize('UTC').tz_convert(timezone)

    # figure out which row is the first row with non-zero bikes available
    non_zero_row = 0
    
    while station_df.ix[non_zero_row,"bikes_available"] == 0:
        non_zero_row += 1
    #print non_zero_row
    # subset data we drop all the leading rows with zeros in available_bikes
    station_df_non_zero_row = station_df.ix[non_zero_row:,]
    
    #put all data into 15 minute buckets, since some data was collected every 2 minutes and some every minute
    station_bucketed = station_df_non_zero_row.resample(str(time_agg_level)+'MIN', how = agg_type)
    
    # Drop rows that have missing observations for bikes_available or slots_available
    station_bucketed = station_bucketed[np.isfinite(station_bucketed['bikes_available'])]
    station_bucketed = station_bucketed[np.isfinite(station_bucketed['slots_available'])]
    return station_bucketed

# <codecell>

# test
#dc_17=fetch_station("Washington, D.C.", 17, 15, 'max')

# <codecell>

#dc_17.head()

# <codecell>

#dc_17.ix[:,"preciptype"].value_counts()

# <codecell>

#dc_17.ix[:,"preciptype" == "rain"]
#dc_17["2010-10-06"]

# <codecell>


