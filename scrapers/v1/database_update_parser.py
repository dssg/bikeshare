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
##This function connects to the data base (through enviornment varibles), gets the data from a provided url
def main(url,city):
    try:
        conn = psycopg2.connect(dbname=+os.environ.get('dbname'),user=+os.environ.get('dbuser'), host=+os.environ.get('dburl'),database=bikeshare)
    except:
        print "I am unable to connect to the database"
    cur = conn.cursor()
    
    r = requests.get(url)

    fulltext = r.text

    soup = BeautifulSoup(fulltext)

    for station in soup.find_all("station"):
        ident = long(extract_str(station.find("id")))
        bikes = long(extract_str(station.find("nbbikes")))
        stations = long(extract_str(station.find("nbemptydocks")))
        timestamp = datetime.datetime.utcnow()
        if (city.lower() == 'boston'):
            cur.execute("""INSERT INTO bike_ind_boston (tfl_id, bikes, spaces) VALUES (%s, %s,%s);""",(ident,bikes,stations))
        elif (city.lower() == "washingtondc"):
            cur.execute("""INSERT INTO bike_ind_washingtondc (tfl_id, bikes, spaces, timestamp) VALUES (%s, %s,%s,%s);""",(ident, bikes,stations,timestamp))
        elif (city.lower() == "minneapolis"):
            cur.execute("""INSERT INTO bike_ind_minneapolis (tfl_id, bikes, spaces, timestamp) VALUES (%s, %s,%s,%s);""",(ident, bikes,stations,timestamp))
        else:
            print "no city info supplied"
    conn.commit()
    #print timestamp

# #urls = ("http://www.thehubway.com/data/stations/bikeStations.xml", "https://secure.niceridemn.org/data2/bikeStations.xml",
#        "http://www.capitalbikeshare.com/data/stations/bikeStations.xml")

##parameters URL and City [boston,washingtondc,minneapolis]
main(argv[1],argv[2])
    
