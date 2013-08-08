import pandas as pd
from pandas.tseries.offsets import * 
import numpy as np
# Modelfit should output a function that will function on a dateframe indexed by timestamp

	# Probabilities vector of length n+1 where n is number of stations
# startdate can be formatted as a string of minimum length so  "m/d/yyyy" if possible.
 ### worst case is that startdate looks like 'mm/dd/yyyy'

def model_validation(modelfit, int n, startdate=None, data):
	# If no explicit startdate is given, use the first date 
	if startdate == None:
		startdate = data.index[0]
	else:
		try:
			startdate = data[startdate:].index[0]
		except:
			print "That date is after the end of biketime. We'll choose the first date in our dataset."
			startdate = data.index[0]

	# Set the initial end-date.
	enddate = startdate + DateOffset(years = 1)

	# Amount of time by which to shift in re-fitting
	offset = DateOffset(weeks=1, days=1, hours=1)
	# WHILE LOOPS ARE EVIL!
	for i in range(10000):
		if i != 0:
			enddate += offset
		
		try:
			test_data = true_test_data = data[(np.datetime64(enddate):].iloc[1:7] # The time we begin testing on
		except: 
			break
		else:
			print "Training on data up to %s" % str(enddate)

		fit_data = data[np.datetime64(startdate):np.datetime64(enddate)]
		model = modelfit(fit_data, n) # Should return a function that will predict based on a dateframe
		print "Steps Out, Expected Number of Bikes, True Expected Number of Bikes, MSE"
		for i in range(3)

			(lst_prob, ev_bikes) = model(test_data.iloc[i:(i+3)]) # Run the model on three lags out (so done of the data we predict is in our training sample)
			# Evaluate empirical probability
			

			ev_slots = n - ev_bikes
			test_data.iloc[i+3]["bikes_available"] = ev_bikes
			test_data.iloc[i+3]["slots_available"] = ev_slots
			true_bikes = true_test_data.iloc[i+3]["bikes_available"]
			mse = pow((ev_bikes - true_bikes),2)
			print "%d, %d, %d, %f" % (i, ev_bikes, true_bikes, mse)


			#print "%d,%f,%f" % ((i+1), lst_prob[0], lst_prob[-1])



