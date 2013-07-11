## Update Scripts BIXI V1 ##
============================

The update scripts are responsible for keeping the database up to data by each minute. `update_script.sh` should be added to the crontab at 1 minute intervals. 

`update_script.sh` calls `python database_update_parser.py http://abikesharesite.com/data/xml city_for_bikeshare`

The database configurations must be set in the environment varibles. 
