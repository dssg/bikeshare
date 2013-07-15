# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

import os
import psycopg2
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

# Initialize pdf document for later printing
pdf_pages = Pdfpages('Boston_annual_average.pdf');

conn = psycopg2.connect("dbname="+os.environ.get('dbname')+" user="+os.environ.get('dbuser')+ " host="+os.environ.get('dburl'))

cur = conn.cursor()

cur.execute("SELECT DISTINCT(id) FROM metadata_boston;")

stations = list(cur.fetchall())

cur.execute(
            "prepare myplan as "
            "select * from bike_ind_boston where tfl_id = $1")
for i in stations:
    print "i is equal to %d" % i
    cur.execute("execute myplan (%s)", i)
    station = cur.fetchall()
    
    timezone = 'US/Eastern'
    
    station_df = pd.DataFrame.from_records(station, columns = ["station_id", "bikes_available", "slots_available", "timestamp"], index = ["timestamp"])
    
    # Change time from UTC to timezone of bikeshare city
    station_df.index.tz_localize('UTC').tz_convert(timezone)
    
    # Bucket our observations into two minute intervals
    # We need to do this because historical data is sampled every other minute while new data is every minute.

    station_bucketed = station_df.resample("2MIN")
    
    # Group by minute value (i.e. how many minutes have occured since midnight)
    station_annual_groups = station_bucketed.groupby(station_bucketed.index.map(lambda t: 60*t.hour + t.minute))
    
    # Take the mean over each minute-since-midnight group
    station_annual_averages = station_annual_groups.mean()
    
    # Takes the converted minute value and displays it as a readable time
    def minute_into_hour(x):
        if x % 60 in range(0,10):
            return str(x // 60) + ":0" + str(x % 60)
        else:
            return str(x // 60) + ":" + str(x % 60)
        
    times = station_annual_averages.index.map(minute_into_hour)
    
    # Add these new time values into our dataframe
    station_annual_averages["timestamp"] = times
    
    # Plot the time against the number of bikes available
    station_plot =  station_annual_averages.plot(x = 'timestamp', y = 'bikes_available')
    plt.savefig('station_'+str(i[0])+'.pdf')

# <codecell>


