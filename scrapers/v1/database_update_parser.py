import requests
from bs4 import BeautifulSoup
from types import NoneType
from sys import argv
import os
import datetime
import calendar
import psycopg2 

def extract_str(element):
    if type(element) is NoneType:
        return element
    else:
        return element.string

def main(url,city):
    city_db
    if (city == "boston"):
        city_db = "bike_ind_boston"
    if (city == "washingtondc"):
        city_db = "bike_ind_washingtondc"
    if (city == "minneapolis"):
        city_db = "bike_ind_minneapolis"
    else:
        print "no city info supplied"

    try:
        conn = psycopg2.connect("dbname="+os.environ.get('dbname')+" user="+os.environ.get('dbuser')+ " host="+os.environ.get('dburl'))
    except:
        print "I am unable to connect to the database"
    r = requests.get(url)

    fulltext = r.text

    soup = BeautifulSoup(fulltext)
    print soup.find_all("station")[1]
    for station in soup.find_all("station"):
        ident = extract_str(station.find("id"))
        bikes = extract_str(station.find("nbbikes"))
        stations = extract_str(station.find("nbemptydocks"))
        timestamp = datetime.datetime.utcnow()
        #print "{0},{1},{2},{3}".format(ident, bikes, stations, timestamp)
        cur = conn.cursor()
        cur.execute(
...     """INSERT INTO %s (tfl_id, bikes, spaces, timestamp)
...         VALUES (%s, %s, %s,%s);""",
...     (city_db, ident, bikes,stations,timestamp))
        



# #urls = ("http://www.thehubway.com/data/stations/bikeStations.xml", "https://secure.niceridemn.org/data2/bikeStations.xml",
#        "http://www.thehubway.com/data/stations/bikeStations.xml")

main(argv[1],argv[2])
    
