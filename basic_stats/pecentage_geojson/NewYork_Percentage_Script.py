# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

import json
import psycopg2
import os
import operator 
import geojson


#psycopg2 
try:
    conn = psycopg2.connect("dbname="+os.environ.get('dbname')+" user="+os.environ.get('dbuser')+ " host="+os.environ.get('dburl'))
except:
    print "I am unable to connect to the database"
cur = conn.cursor()

cur.execute("SELECT DISTINCT tfl_id FROM bike_ind_newyork LIMIT 5;");

stations = cur.fetchall()

#stations = map(operator.itemgetter(0), stations)

station_records_total = []
# Modify this for other cities to reflect new staions opening. 
cur.execute(
    "prepare totalcount as "
    "SELECT COUNT (timestamp) FROM bike_ind_newyork WHERE tfl_id = $1;")
for i in stations:
    cur.execute("execute totalcount (%s)",i)
    for record in cur:
        station_records_total.append((record,i))


station_records_no_bikes = []
station_records_no_spaces = []
stations_metadata = []


#Get number times there are no bikes
cur.execute(
    "prepare bikeszero as "
    "SELECT COUNT(timestamp) FROM bike_ind_newyork WHERE tfl_id = $1 AND bikes = 0;")
for i in stations:
    cur.execute("execute bikeszero (%s)", i)
    for record in cur:
        station_records_no_bikes.append((record,i))
print "query 2 done"

#number of times there are spaces
cur.execute(
    "prepare spaceszero as "
    "SELECT COUNT(timestamp) FROM bike_ind_newyork WHERE tfl_id = $1 AND spaces = 0;")
for i in stations:
    cur.execute("execute spaceszero (%s)", i)
    for record in cur:
        station_records_no_spaces.append((record,i))
 
#gets the metadata
cur.execute(
    "prepare metadata as "
    "SELECT * FROM metadata_newyork WHERE id = $1;")
for i in stations:
    cur.execute("execute metadata (%s)",i)
    for record in cur:
        stations_metadata.append((record,i))
        
print "queries done"

print station_records_total
print station_records_no_bikes
print station_records_no_spaces
print stations_metadata

# <codecell>

station_record_dict = {}
for station in station_records_total:
    record = station[0][0]
    id = int(station[1][0])
    station_record_dict[id] = record

print station_record_dict

#initilization 
empty_dict = {}
full_dict = {}
name_dict = {}
point_dict = {}

for x in station_records_no_bikes:
    empty_time = (float(x[0][0]) / station_records_total[0][0]) * 100  #get percentage of time each station is empty
    id = x[1][0]
    empty_dict[id] = empty_time
    
for x in station_records_no_spaces:
    full_time = (float(x[0][0]) / station_records_total[0][0]) * 100 # get pecentage of time each station is full
    id = x[1][0]
    full_dict[id] = full_time

for x in stations_metadata:
    point = geojson.Point([x[0][3],x[0][2]])
    name = x[0][1]
    id = x[1][0]
    name_dict[id] = name
    point_dict[id] = point
    
print empty_dict
print name_dict
print point_dict

#get keys
key_list = empty_dict.keys()
print key_list

#empty feature collection (a geojson feature)
feature_collection = {"type": "FeatureCollection",
                      "features": []
                      }


#to GEOJSON
for key in key_list:
    feature_collection["features"].append({"type":"Feature","geometry":point_dict[key],"properties":{"name":name_dict[key], "percentage_empty": empty_dict[key], "percentage_full":full_dict[key]}})


print geojson.dumps(feature_collection)


# <codecell>


# <codecell>


# <codecell>


