Data Documentation
===================

`clean_data.sh` turns the .tsv files from MySQL dumps into .csv for postgres import. The mysql dumps came from Oliver O'Brien's database. 

`create_db.sql` creates appropriate tables and then imports the appropriate .csvs into the database. 

`models.py` is an work in progress. Eventually, it should be [SQLAlechemy](http://www.sqlalchemy.org/) models for bikeshare data.

Please see the [data section of the Wiki](https://github.com/dssg/bikeshare/wiki/data) for more information.