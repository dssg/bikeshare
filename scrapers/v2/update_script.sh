#!/bin/bash

source /etc/bashrc

python /home/ubuntu/bikeshare/scrapers/v2/database_scraper.py http://divvybikes.com/stations/json chicago
python /home/ubuntu/bikeshare/scrapers/v2/database_scraper.py http://citibikenyc.com/stations/json newyork
