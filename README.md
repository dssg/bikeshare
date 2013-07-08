bikeshare
=========

Bikeshare repo

The data is based off of Divy Data, in minute by minute snapshots.

**There are two Divy systems, DivyV1 (Boston, Washington DC & Minneapolis) and DivyV2 (Chicago and New York City)**

###Schema, DivyV1

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

###Schema, DivyV2
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

### Notes	
The difference in ordering is a known, legacy issue. 

Total docks (V2 Only) = unavailable docks (presumed bike marked as broken or dock itself broken) + bikes + spaces.


While we are on the topic, note that the timestamp I report is my own timestamp rather than an operator-supplied timestamp. The two should normally agree to within a couple of minutes, except if the operator is having system issue which causes the feed to still be available but not update.

I also don't currently record dock statuses (e.g. temporary, active, locked, bonus), locations, names, addresses, or other available metadata.


