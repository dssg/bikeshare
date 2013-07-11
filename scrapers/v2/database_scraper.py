import json
import requests
import datetime
import time
import os
import psycopg2
import urllib
from sys import argv


#get url
url = argv[1]
city = argv[2]

#convert JSON to object and get from URL
as_data = urllib.urlopen(url).read()
data = json.loads(as_data)

data = json.loads(as_data)

J2 = data["stationBeanList"]

#psycopg2 
try:
    conn = psycopg2.connect("dbname="+os.environ.get('dbname')+" user="+os.environ.get('dbuser')+ " host="+os.environ.get('dburl'))
except:
    print "I am unable to connect to the database"
cur = conn.cursor()

#loop and insert   
for j in J2:
    indent = long(j["id"])
    bikes = long(j["availableDocks"])
    stations = long(j["availableBikes"])
    totalDocks = long(j["totalDocks"])
    if (city.lower() == 'chicago'):
        cur.execute("""INSERT INTO bikes_ind_chicago (tfl_id,bikes,spaces,totat_docks) VALUES (%s,%s,%s,%s)""",(indent,bikes,stations,totalDocks))
    elif (city.lower() == 'newyork'):
        cur.execute("""INSERT INTO bikes_ind_newyork (tfl_id,bikes,spaces,totat_docks) VALUES (%s,%s,%s,%s)""",(indent,bikes,stations,totalDocks))
    else:
        print "No city suppied"

conn.commit()