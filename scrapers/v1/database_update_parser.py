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
    if (city == "boston"):
        city_db = "bike_ind_boston"
    elif (city == "washingtondc"):
        city_db = "bike_ind_washingtondc"
    elif (city == "minneapolis"):
        city_db = "bike_ind_minneapolis"
    else:
        print "no city info supplied"

    try:
        conn = psycopg2.connect("dbname="+os.environ.get('dbname')+" user="+os.environ.get('dbuser')+ " host="+os.environ.get('dburl'))
    except:
        print "I am unable to connect to the database"
    cur = conn.cursor()
    try:
        cur.execute("""SELECT * from bike_ind_boston LIMIT 5;""")
    except:
        print "I can't SELECT from bar"

    rows = cur.fetchall()
    print "\nShow me the databases:\n"
    for row in rows:
        print "   ", row[0]

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
        cur.execute("""INSERT INTO """+city_db+""" (tfl_id, bikes, spaces, timestamp) VALUES (%s, %s,%s,%s);""", (ident, bikes,stations,timestamp))   

    print timestamp
    print city_db
# #urls = ("http://www.thehubway.com/data/stations/bikeStations.xml", "https://secure.niceridemn.org/data2/bikeStations.xml",
#        "http://www.thehubway.com/data/stations/bikeStations.xml")

main(argv[1],argv[2])
    
