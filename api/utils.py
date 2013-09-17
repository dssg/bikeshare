#a series of utility functions (ie, validators)
# for the API

def valid_city(city):
	city_list = ["bayarea","boston","washingtondc","newyork","chicago","minneapolis"]
	if city not in city_list:
		return False
	else
		return True

def valid_month(month):
	if month not in range(1,12):
		return False
	else
		return True

def valid_day(day):
	if day not in range (1,31):
		return False
	else
		return True

def valid_year(year):
	if year < 2010:
		return False
	else
		return True