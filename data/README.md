Data Documentation
===================

Alta's real-time bike APIs only publish current bike availability data, not historical. We got historical data as mysql dumps from urban researcher Oliver O'Brien. 

- `clean_data.sh` turns the .tsv files from MySQL dumps into .csv for import into our PostgreSQL db.

- `create_db.sql` builds our postgreSQL db from the cleaned historical data. it creates appropriate tables and then imports the appropriate .csv files into them. the scripts in `scrapers` add historical weather data to this database to fill it out. they also add current bike availability and weather to keep it up to date.

- `models.py` is an work in progress. Eventually, it should be [SQLAlechemy](http://www.sqlalchemy.org/) models this database to make it easier to use.

Please see the [data section of the Wiki](https://github.com/dssg/bikeshare/wiki/data) for more information.
