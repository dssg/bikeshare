#!/bin/bash

# This script cleans up the raw data from Oliver O'Brien's mysql database. Run this before inserting
# csv's into the database.

perl -lpe 's/"/""/g; s/^|$/"/g; s/\t/","/g' < bike_ind_minneapolis.csv > bike_ind_minneapolis_c.csv
perl -lpe 's/"/""/g; s/^|$/"/g; s/\t/","/g' < bike_agg_minneapolis.csv > bike_agg_minneapolis_c.csv
echo "done with minneapolis"
perl -lpe 's/"/""/g; s/^|$/"/g; s/\t/","/g' < bike_ind_newyork.csv > bike_ind_newyork_c.csv
perl -lpe 's/"/""/g; s/^|$/"/g; s/\t/","/g' < bike_agg_newyork.csv > bike_agg_newyork_c.csv
echo "done with NY"
perl -lpe 's/"/""/g; s/^|$/"/g; s/\t/","/g' < bike_ind_boston.csv > bike_ind_boston_c.csv
perl -lpe 's/"/""/g; s/^|$/"/g; s/\t/","/g' < bike_agg_boston.csv > bike_agg_boston_c.csv
echo "done with Bos"
perl -lpe 's/"/""/g; s/^|$/"/g; s/\t/","/g' < bike_ind_chicago.csv > bike_ind_chicago_c.csv
perl -lpe 's/"/""/g; s/^|$/"/g; s/\t/","/g' < bike_agg_chicago.csv > bike_agg_chicago_c.csv
echo "done with chicago"
perl -lpe 's/"/""/g; s/^|$/"/g; s/\t/","/g' < bike_ind_washingtondc.csv > bike_ind_washingtondc_c.csv
perl -lpe 's/"/""/g; s/^|$/"/g; s/\t/","/g' < bike_agg_washingtondc.csv > bike_agg_washingtondc_c.csv
echo "finished"
