## Update Scripts for BIXI V2 JSON API
---

- `database_scraper.py`: when called, fetches current bike share station status for cites that use Alta's version 2 JSON API and adds them to PostgreSQL database. The database configurations must be set in the environment varibles. You will need to configure `dburl`,`dbname` and `dbuser` to the appropriate values for your specific Postgres install.
- `update_script.sh` keeps the database up to data by each minute. It should be added to the crontab at 1 minute intervals. 

`update_script.sh` calls `python database_scraper.py http://abikesharesite.com/data/xml city_for_bikeshare`
