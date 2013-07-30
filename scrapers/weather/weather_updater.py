import os
import json
import urllib2
import time
import datetime
from forecastio import forecastio 
import psycopg2

#Set the LAT/LONG for each city
boston = (42.3587,-71.0567)
washingtondc = (38.8900, -77.0300)
minneapolis = (44.9800,-93.2636)
newyork = (40.7142,-74.0064)
chicago = (41.8500,-87.6500)

#Connect to DB
try:
  conn = psycopg2.connect("dbname="+os.environ.get('dbname')+" user="+os.environ.get('dbuser')+ " host="+os.environ.get('dburl'))
except:
  print "I am unable to connect to the database"
  exit()
cur = conn.cursor()

forecast = forecastio.Forecastio(str(os.environ.get('FORECASTIOKEY')))

#GRab the Forecast from the Forecast.IO Api and Current
boston_forcast = forecast.load_forecast(boston[0],boston[1])
boston_c = forecast.get_currently()
washingtondc_forecast = forecast.load_forecast(washingtondc[0],washingtondc[1])
washingtondc_c = forecast.get_currently()
minneapolis_forecast = forecast.load_forecast(minneapolis[0],minneapolis[1])
minneapolis_c = forecast.get_currently()
newyork_forecast = forecast.load_forecast(newyork[0],newyork[1])
newyork_c = forecast.get_currently()
chicago_forecast = forecast.load_forecast(chicago[0],chicago[1])
chicago_c = forecast.get_currently()

#Get the "current" subobj and shove into the db
cur.execute("""INSERT INTO weather_boston (time,summary,precipIntensity,precipProbability,precipType,precipAccumulation,temperature) VALUES
    (%s,%s,%s,%s,%s,%s,%s);""",
    (boston_c.time,boston_c.summary,boston_c.precipIntensity,boston_c.precipProbability,
    	boston_c.precipType,boston_c.precipAccumulation,boston_c.temperature))

cur.execute("""INSERT INTO weather_washingtondc (time,summary,precipIntensity,precipProbability,precipType,precipAccumulation,temperature) VALUES
    (%s,%s,%s,%s,%s,%s,%s);""",
    (washingtondc_c.time,washingtondc_c.summary,washingtondc_c.precipIntensity,washingtondc_c.precipProbability,
    	washingtondc_c.precipType,washingtondc_c.precipAccumulation,washingtondc_c.temperature))

cur.execute("""INSERT INTO weather_minneapolis (time,summary,precipIntensity,precipProbability,precipType,precipAccumulation,temperature) VALUES
    (%s,%s,%s,%s,%s,%s,%s);""",
    (minneapolis_c.time,minneapolis_c.summary,minneapolis_c.precipIntensity,minneapolis_c.precipProbability,
    	minneapolis_c.precipType,minneapolis_c.precipAccumulation,minneapolis_c.temperature))

cur.execute("""INSERT INTO weather_newyork (time,summary,precipIntensity,precipProbability,precipType,precipAccumulation,temperature) VALUES
    (%s,%s,%s,%s,%s,%s,%s);""",
    (newyork_c.time,newyork_c.summary,newyork_c.precipIntensity,newyork_c.precipProbability,
    	newyork_c.precipType,newyork_c.precipAccumulation,newyork_c.temperature))

cur.execute("""INSERT INTO weather_chicago (time,summary,precipIntensity,precipProbability,precipType,precipAccumulation,temperature) VALUES
    (%s,%s,%s,%s,%s,%s,%s);""",
    (chicago_c.time,chicago_c.summary,chicago_c.precipIntensity,chicago_c.precipProbability,
    	chicago_c.precipType,chicago_c.precipAccumulation,chicago_c.temperature))

# commit the changes
conn.commit()