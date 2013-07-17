import os
import json
import urllib2
import time
import csv

citylatlong="/42.3587,-71.0567,"

def my_range(start, end, step):
    while start <= end:
        yield start
        start += step
days = {}
#realstart 1262304000
for x in my_range(1372636800,time.time(),86400):
	url = 'https://api.forecast.io/forecast/'+os.environ.get('FORECASTIOKEY')+citylatlong+str(int(time.time()))
	response = urllib2.urlopen(url)
	json_dict = json.load(response)
	days[x] = json_dict['daily']['data']

print "time,summary,icon,sunriseTime,sunsetTime,precipType,temperatureMin,temperatureMin,temperatureMax,temperatureMaxTime,dewPoint,windSpeed,windBearing,humidity,pressure"
for time in days.keys():
	print str(days[time][0]['time'])+','+days[time][0]['summary']+','+days[time][0]['icon']+','+str(days[time][0]['sunriseTime'])+','+str(days[time][0]['sunsetTime'])+','+days[time][0]['precipType']+','+str(days[time][0]['temperatureMin'])+','+str(days[time][0]['temperatureMin'])+','+str(days[time][0]['temperatureMax'])+','+str(days[time][0]['temperatureMaxTime'])+','+str(days[time][0]['dewPoint'])+','+str(days[time][0]['windSpeed'])+','+str(days[time][0]['windBearing'])+','+str(days[time][0]['humidity'])+','+str(days[time][0]['pressure'])