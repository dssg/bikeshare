#!/bin/bash

source /etc/bashrc

python /home/ec2-user/bikeshare/scrapers/v1/database_update_parser.py http://www.thehubway.com/data/stations/bikeStations.xml boston
python /home/ec2-user/bikeshare/scrapers/v1/database_update_parser.py https://secure.niceridemn.org/data2/bikeStations.xml minneapolis
python /home/ec2-user/bikeshare/scrapers/v1/database_update_parser.py http://www.capitalbikeshare.com/data/stations/bikeStations.xml washingtondc