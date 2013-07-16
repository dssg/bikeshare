
import os
import psycopg2
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.dates as dates

conn = psycopg2.connect("dbname="+os.environ.get('dbname')+" user="+os.environ.get('dbuser')+ " host="+os.environ.get('dburl'))

cur = conn.cursor()

cur.execute("SELECT id, name FROM metadata_boston;")

stations = list(cur.fetchall())
stations = stations

# Initialize pdf document for later printing
pdf_pages = PdfPages('Boston_annual_average.pdf');
nb_plots = len(stations)
print "nb_plots = %s" % str(nb_plots)
nb_plots_per_page = 5
nb_pages = nb_plots/nb_plots_per_page
print "nb_pages = %s" % str(nb_pages)
grid_size = (5,1)


cur.execute(
            "prepare myplan as "
            "select * from bike_ind_boston where tfl_id = $1")
for count, i in enumerate(stations):
    print str(i)
    cur.execute("execute myplan (%s)", (i[0],))
    station = cur.fetchall()
    
    timezone = 'US/Eastern'
    
    station_df = pd.DataFrame.from_records(station, columns = ["station_id", "bikes_available", "slots_available", "timestamp"], index = ["timestamp"])
    
    # Change time from original timezone to timezone of bikeshare city
    station_df['7/5/2013':].index.tz_localize('UTC').tz_convert(timezone)
    station_df.index.tz_localize(timezone)
    
    # Bucket our observations into two minute intervals
    # We need to do this because historical data is sampled every other minute while new data is every minute.

    station_bucketed = station_df.resample("2MIN")
    
    # Group by minute value (i.e. how many minutes have occured since midnight)
    station_annual_groups = station_bucketed.groupby(station_bucketed.index.map(lambda t: 60*t.hour + t.minute))
    
    # Take the mean over each minute-since-midnight group
    station_annual_averages = station_annual_groups.mean()
    station_annual_std = station_annual_groups["bikes_available"].std()
    
    # Takes the converted minute value and displays it as a readable time
    def minute_into_hour(x):
        if x % 60 in range(0,10):
            return str(x // 60) + ":0" + str(x % 60)
        else:
            return str(x // 60) + ":" + str(x % 60)
        
    times = station_annual_averages.index.map(minute_into_hour)
    times_std = station_annual_std.index.map(minute_into_hour)
    
    # Add these new time values into our dataframe
    station_annual_averages["timestamp"] = times
    station_annual_averages["bikes_available_std"] = station_annual_std
    
    # Plot the time against the number of bikes available

    # Check whether we need to start a page
    if count % nb_plots_per_page == 0:
        fig = plt.figure(figsize=(11,17),dpi=100)
    fig.suptitle('Average Bikes Available By Time of Day')
    # Actually plot the things
    ax = plt.subplot2grid(grid_size, (count % nb_plots_per_page,0))
    t = pd.to_datetime(station_annual_averages['timestamp'])
    mu1 = station_annual_averages['bikes_available']
    sigma1 = station_annual_averages['bikes_available_std']

    ax.plot(t, mu1)
    
    # Uncomment this line to add error-bars
    #ax.fill_between(t, (mu1+sigma1).tolist(), (mu1-sigma1).tolist(), facecolor='blue', alpha=0.5)
    ax.xaxis.set_major_formatter(dates.DateFormatter('%H:%M'))
    plt.setp(plt.xticks()[1], rotation=30)
    #station_plot =  station_annual_averages.plot(x = 'timestamp', y = 'bikes_available')
    station_name = str(stations[count][1])
    ax.set_title(station_name)
    plt.xlabel('Time of Day')
    plt.ylabel('Average Available Bikes')

    # Close the page if needed
    if (count + 1) % nb_plots_per_page == 0 or (count + 1) == nb_plots:
        plt.tight_layout()
        pdf_pages.savefig(fig)


pdf_pages.close()
