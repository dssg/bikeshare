SET timezone TO "+00:00";     

CREATE TABLE IF NOT EXISTS bike_agg_minneapolis (                                         
  timestamp timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,                                             
  bikes integer NOT NULL,                                                                             
  spaces integer NOT NULL,                                                                            
  unbalanced integer NOT NULL                                                                         
);

CREATE TABLE IF NOT EXISTS bike_ind_minneapolis (
  tfl_id integer NOT NULL,
  bikes integer NOT NULL,
  spaces integer NOT NULL,
  timestamp timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (tfl_id,timestamp),
  KEY timestamp
);

CREATE TABLE IF NOT EXISTS bike_agg_boston (                                         
  timestamp timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,                                             
  bikes integer NOT NULL,                                                                             
  spaces integer NOT NULL,                                                                            
  unbalanced integer NOT NULL                                                                         
);

CREATE TABLE IF NOT EXISTS bike_ind_boston (
  tfl_id integer NOT NULL,
  bikes integer NOT NULL,
  spaces integer NOT NULL,
  timestamp timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (tfl_id,timestamp),
  KEY timestamp
);

CREATE TABLE IF NOT EXISTS bike_agg_newyork (                                         
  timestamp timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,                                             
  bikes integer NOT NULL,                                                                             
  spaces integer NOT NULL,                                                                            
  unbalanced integer NOT NULL                                                                         
);

CREATE TABLE IF NOT EXISTS bike_ind_newyork (
  tfl_id integer NOT NULL,
  bikes integer NOT NULL,
  spaces integer NOT NULL,
  timestamp timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (tfl_id,timestamp),
  KEY timestamp
);

CREATE TABLE IF NOT EXISTS bike_agg_chicago (                                         
  timestamp timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,                                             
  bikes integer NOT NULL,                                                                             
  spaces integer NOT NULL,                                                                            
  unbalanced integer NOT NULL                                                                         
);

CREATE TABLE IF NOT EXISTS bike_ind_chicago (
  tfl_id integer NOT NULL,
  bikes integer NOT NULL,
  spaces integer NOT NULL,
  timestamp timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (tfl_id,timestamp),
  KEY timestamp
);

CREATE TABLE IF NOT EXISTS bike_agg_washingtondc (                                         
  timestamp timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,                                             
  bikes integer NOT NULL,                                                                             
  spaces integer NOT NULL,                                                                            
  unbalanced integer NOT NULL                                                                         
);

CREATE TABLE IF NOT EXISTS bike_ind_washingtondc (
  tfl_id integer NOT NULL,
  bikes integer NOT NULL,
  spaces integer NOT NULL,
  timestamp timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (tfl_id,timestamp),
  KEY timestamp
);

\copy bike_agg_minneapolis FROM '/mnt/data1/BikeShare/raw_data/casa.oobrien.com/misc/bikedata/bike_agg_minneapolis_c.csv' DELIMITER ',' CSV; 
\copy bike_ind_minneapolis FROM '/mnt/data1/BikeShare/raw_data/casa.oobrien.com/misc/bikedata/bike_ind_minneapolis.csv' DELIMITER ',' CSV;