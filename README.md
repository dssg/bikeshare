bikeshare
=========

Bikeshare repo

The data is based off of BIXI Data, in minute by minute snapshots.

**There are two BIXI systems, BIXIV1 (Boston, Washington DC & Minneapolis) and BIXIV2 (Chicago and New York City)**

###Schema, BIXIV1

* Indiv
	* tfl_id 
	* bikes
	* spaces      
	* timestamp   
* Agg 
	* timestamp     
	* bikes
	* spaces
	* unbalanced 

###Schema, BIXIV2
* Indiv
	* tfl_id   
	* bikes
	* spaces 
	* total_docks 
	* timestamp
* Agg
 	* timestamp    
	* bikes
	* spaces 
	* unbalanced
	* total_docks 

### Scrapers
Scrapers are built to get the metadata for the database. Many thanks to Anna Meredith & [Patrick Collins](https://github.com/capitalsigma) for their code contributions on this. 

### Notes	
The difference in ordering is a known, legacy issue. 

Total docks _(V2 Only)_ = unavailable docks (presumed bike marked as broken or dock itself broken) + bikes + spaces.


While we are on the topic, note that the timestamp I report is my own timestamp rather than an operator-supplied timestamp. The two should normally agree to within a couple of minutes, except if the operator is having system issue which causes the feed to still be available but not update.

I also don't currently record dock statuses (e.g. temporary, active, locked, bonus), locations, names, addresses, or other available metadata.



