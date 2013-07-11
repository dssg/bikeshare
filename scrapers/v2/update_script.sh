#!/bin/bash

source /etc/bashrc

python /home/ec2-user/bikeshare/scrapers/v2/database_scraper http://divvybikes.com/stations/json chicago
