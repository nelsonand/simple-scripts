#Downloading weather data using Python as a json using the Visual Crossing Weather API
#See https://www.visualcrossing.com/resources/blog/how-to-load-historical-weather-data-using-python-without-scraping/ for more information.
import csv
import json
import codecs
import urllib.request
import urllib.error
import sys

#### INPUTS ####

# Location for the weather data
Location = 'PagosaSpings,CO'

# Set start and end dates
StartDate = '2010-01-01'
EndDate = '2012-01-01'

#### DEFAULTS ####

# This is the core of our weather query URL
BaseURL = 'https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/'

# Find ApiKey at https://www.visualcrossing.com/account
ApiKey = 'F9MR7UC95UN96HBGN63R39J26'

# UnitGroup sets the units of the output - us or metric
UnitGroup = 'us'

#JSON or CSV
ContentType = "json"

#include sections
#values include days,hours,current,alerts
Include = "days"

#### GET DATA ####

print('')
print(' - Requesting weather...')

#basic query including location
ApiQuery=BaseURL + Location

#append the start and end date if present
if (len(StartDate)):
    ApiQuery+="/"+StartDate
    if (len(EndDate)):
        ApiQuery+="/"+EndDate

#Url is completed. Now add query parameters (could be passed as GET or POST)
ApiQuery+="?"

#append each parameter as necessary
if (len(UnitGroup)):
    ApiQuery+="&unitGroup="+UnitGroup

if (len(ContentType)):
    ApiQuery+="&contentType="+ContentType

if (len(Include)):
    ApiQuery+="&include="+Include

ApiQuery+="&key="+ApiKey

print(' - Running query URL: ', ApiQuery)
print()

try:
    ResultBytes = urllib.request.urlopen(ApiQuery).read()
    # Parse the results as JSON
    jsonData = json.loads(ResultBytes.decode('utf-8'))
except urllib.error.HTTPError  as e:
    ErrorInfo= e.read().decode()
    print('Error code: ', e.code, ErrorInfo)
    sys.exit()
except  urllib.error.URLError as e:
    ErrorInfo= e.read().decode()
    print('Error code: ', e.code,ErrorInfo)
    sys.exit()

#### SAVE DATA ####

with open('weather-plotter/histData/data_'+Location+'_'+StartDate+'_'+EndDate+'.json', 'w') as f:
    json.dump(jsonData, f)
