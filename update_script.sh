#!/bin/bash

source /etc/bashrc

python xml_metadata_parser.py http://www.thehubway.com/data/stations/bikeStations.xml boston
python xml_metadata_parser.py https://secure.niceridemn.org/data2/bikeStations.xml minneapolis
python xml_metadata_parser.py http://www.capitalbikeshare.com/data/stations/bikeStations.xml washingtondc