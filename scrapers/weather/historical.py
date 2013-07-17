import os
import json
import urllib2
import time
import csv
import datetime
from forecastio import forecastio 

city_lat  = 42.3587
city_long = -71.0567


forecast = forecastio.Forecastio(str(os.environ.get('FORECASTIOKEY')))
result = forecast.load_forecast(city_lat,city_long)

start_date = datetime.datetime(2011,1,1)
end_date = datetime.datetime(2013,7,17)
d = start_date
delta = datetime.timedelta(days=1)

myfile = open('weather_data_boston.csv', 'wb')
wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
header_list = ["time","summary","icon","sunriseTime","sunsetTime","precipIntensity","precipProbability","precipType","precipAccumulation","temperature","temperatureMin","temperatureMinTime","temperatureMax","temperatureMaxTime","humidity"]
wr.writerow(header_list)

while d <= end_date:
    result = forecast.load_forecast(city_lat,city_long,d,lazy=True)
    daily = forecast.get_daily()
    days_list = []
    for item in daily.data:
   		days_list.append(item.time)
   		days_list.append(item.summary)
   		days_list.append(item.icon)
   		days_list.append(item.sunriseTime)
   		days_list.append(item.sunsetTime)
   		days_list.append(item.precipIntensity)
   		days_list.append(item.precipProbability)
   		days_list.append(item.precipType)
   		days_list.append(item.precipAccumulation)
   		days_list.append(item.temperature)
   		days_list.append(item.temperatureMin)
   		days_list.append(item.temperatureMinTime)
   		days_list.append(item.temperatureMax)
   		days_list.append(item.temperatureMaxTime)
   		days_list.append(item.humidity)
    d += delta
    wr.writerow(days_list)


