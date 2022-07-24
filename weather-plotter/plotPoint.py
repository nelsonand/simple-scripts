# A script to plot the json weather data_

import json
import matplotlib.pyplot as plt
import numpy as np

#### INPUTS ####

# Location for the weather data to load from json
Location = 'PagosaSpings,CO'

# Set start and end dates to load from json (YYYY-MM-DD)
StartDate = '2020-01-01'
EndDate = '2022-01-01'

# Set start and end dates for plotting (MMDD)
StartPlot = '0501'
EndPlot = '1001'

#### LOAD DATA ####

with open('weather-plotter/histData/data_'+Location+'_'+StartDate+'_'+EndDate+'.json', 'r') as f:
    jsonData = json.load(f)['days']

#### PROCESS DATA ####

data = {}
want = []
for key in jsonData[0].keys():
    if key == 'datetime':
        data[key] = ['']*len(jsonData)
    if isinstance(jsonData[0][key], float):

        data[key] = ['']*len(jsonData)

for i,item in enumerate(jsonData):
    for key in item:
        if key in data.keys():
            data[key][i] = item[key]


for key in data.keys():
    data[key] = np.array(data[key])

print('Averaging over years...')
days = np.unique([x.split('-')[1] + x.split('-')[2] for x in data['datetime']])
startind = np.where(days==StartPlot)[0][0]
endind = np.where(days==EndPlot)[0][0]
days = days[startind:endind]

def average_over_years(item, data=data, days=days):
    avg = np.zeros(len(days))
    std = np.zeros(len(days))
    datadays = np.array([x.split('-')[1] + x.split('-')[2] for x in data['datetime']])
    for i,day in enumerate(days):
        avg[i] = np.average(data[item][np.where(datadays==day)[0]])
        std[i] = np.std(data[item][np.where(datadays==day)[0]])
    return {'avg':avg, 'std':std}

avgdata = {}
for item in data.keys():
    if item not in ['datetime']:
        avgdata[item] = average_over_years(item)

#### PLOT DATA ####

# plottable keys:
# 'tempmax', 'tempmin', 'temp', 'feelslikemax', 'feelslikemin', 'feelslike',
# 'dew', 'humidity', 'precip', 'precipprob', 'precipcover', 'snow', 'snowdepth',
# 'windspeed', 'winddir', 'pressure', 'cloudcover', 'visibility',
# 'solarradiation', 'solarenergy', 'uvindex', 'moonphase'

plt.figure(figsize=(10,8))
ax1 = plt.subplot(311)
ax2 = plt.subplot(312)
ax3 = plt.subplot(313)

def prettyplot(ax, item, c='k', lw=3, norm=1):
    ax.plot(days, avgdata[item]['avg']/norm, c=c, lw=lw, label=item)
    ax.fill_between(days, (avgdata[item]['avg']-avgdata[item]['std'])/norm, (avgdata[item]['avg']+avgdata[item]['std'])/norm, color=c, alpha=0.3)

prettyplot(ax1, 'tempmax', c='r')
prettyplot(ax1, 'tempmin', c='b')

prettyplot(ax2, 'precip', c='b', norm=0.005)
prettyplot(ax2, 'precipprob', c='c')

prettyplot(ax3, 'cloudcover', c='grey')
prettyplot(ax3, 'solarradiation', c='tomato', norm=6)

# pretty plot
for ax in [ax1, ax2, ax3]:
    ax.legend()

months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
daylabels = [''] * len(days)
for i,day in enumerate(days):
    if day[-2:] == '01':
        daylabels[i] = months[int(day[:2])] + ' ' + '1st'
    if day[-2:] == '15':
        daylabels[i] = months[int(day[:2])] + ' ' + '15th'

ax1.set_xticks([])
ax2.set_xticks([])
ax3.set_xticklabels(daylabels, rotation=45)

plt.show()
