import json 


json_data=open('newyork.json')
data=json.load(json_data)
print "id, stationName, latitude, longitude, statusValue, testStation"
for x in data["stationBeanList"]:
    print str(x["id"])+','+x["stationName"]+','+str(x["latitude"])+','+str(x["longitude"])+','+x["statusValue"]+','+str(x["testStation"])
