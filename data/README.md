Data Documentation
===================

`clean_data.sh` turns the .tsv files from MySQL dumps into .csv for postgres import.

`create_db.sql` creates appropriate tables and then imports the appropriate .csvs into the database. 

`models.py` is an work in progress. Eventually, it should be [SQLAlechemy](http://www.sqlalchemy.org/) models for bikeshare data.