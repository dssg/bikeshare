import urllib2
import re
from BeautifulSoup import BeautifulSoup

# Our url
address ='http://www.capitalbikeshare.com/data/stations/bikeStations.xml'

# Read in the response to a HTTP request
response = urllib2.urlopen(address).read()

# Make a soup object of the website
soup = BeautifulSoup(response)

# Create an output text file
output = open('tfl_id_crosswalk.csv','w')

## Fetch the tfl_id and terminal names
id_lines = soup.fetch('id')
terminal_name_lines = soup.fetch('terminalname')

for i in range(len(id_lines)):
  id_str = str(id_lines[i])
  terminal_str = str(terminal_name_lines[i])

  output.write(re.sub(r'<.*?>','',id_str) + "," + re.sub(r'<.*?>','',terminal_str)+ '\n')

output.close()


