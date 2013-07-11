import requests
from bs4 import BeautifulSoup
from types import NoneType
from sys import argv

def extract_str(element):
    if type(element) is NoneType:
        return ""
    else:
        return element.string

def main(url):
    r = requests.get(url)

    fulltext = r.text

    soup = BeautifulSoup(fulltext)

    for station in soup.find_all("station"):
        ident = extract_str(station.find("id"))
        name = extract_str(station.find("name"))
        lat = extract_str(station.find("lat"))
        longit = extract_str(station.find("long"))
        installed = extract_str(station.find("installed"))
        print "{0},{1},{2},{3},{4}".format(ident, name, lat, longit, installed)


#urls = ("http://www.thehubway.com/data/stations/bikeStations.xml", "https://secure.niceridemn.org/data2/bikeStations.xml",
#        "http://www.thehubway.com/data/stations/bikeStations.xml")

print "{0},{1},{2},{3},{4}".format("id", "name", "lat", "long", "installed")
main(argv[1])
    
