# A script to plot the json weather data, averaged over many files

import json
import matplotlib.pyplot as plt
import numpy as np
import os
import re

#### INPUTS ####

# Location for the weather data to load from json
Location = 'PagosaSpings,CO'

# Set start and end dates for plotting (MMDD)
StartPlot = '0501'
EndPlot = '1001'

# Set location for data files
histDatadir = 'weather-plotter/histData/'
plotdir = 'weather-plotter/plots/'

# #### LOAD DATA ####
files = [x for x in os.listdir(histDatadir) if Location in x]

data = {}
for file in files:
    with open(histDatadir+file, 'r') as f:
         jsonData = json.load(f)['days']

    tmpdata = {}
    for key in jsonData[0].keys():
        if key == 'datetime':
            if key not in data.keys():
                data[key] = []
            tmpdata[key] = ['']*len(jsonData)
        if isinstance(jsonData[0][key], float):
            if key not in data.keys():
                data[key] = []
            tmpdata[key] = ['']*len(jsonData)

    for i,item in enumerate(jsonData):
        for key in item:
            if key in tmpdata.keys():
                tmpdata[key][i] = item[key]

    for key in tmpdata.keys():
        data[key] += tmpdata[key]

#### COMINE AND CLEAN UP ###

keys = list(data.keys())
for key in keys:
    data[key] = np.array(data[key])

for key in keys:
    if len(data[key]) < len(data['datetime']):
        print(f'Warning, {key} not complete... removing from data...')
        del data[key]

#### PROCESS DATA ####

print('Averaging over years...')
days = np.unique([x.split('-')[1] + x.split('-')[2] for x in data['datetime']])

plotstartind = np.where(days==StartPlot)[0][0]
plotendind = np.where(days==EndPlot)[0][0]
plotdays = days[plotstartind:plotendind]

startind = np.where(days=='0401')[0][0]
endind = np.where(days=='1101')[0][0]
days = days[startind:endind]



def average_over_years(item, data=data, days=days):
    avg = np.zeros(len(days))
    std_l = np.zeros(len(days))
    std_u = np.zeros(len(days))
    datadays = np.array([x.split('-')[1] + x.split('-')[2] for x in data['datetime']])
    for i,day in enumerate(days):
        today = np.sort(data[item][np.where(datadays==day)[0]])

        avg[i] = np.average(today)

        std_l[i] = today[round(0.2*len(today))]
        std_u[i] = today[round(0.8*len(today))]

    return {'avg':avg, 'std_l':std_l, 'std_u':std_u}

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

plt.figure(f'Weather{Location}',figsize=(10,8))
ax1 = plt.subplot(311)
ax2 = plt.subplot(312)
ax3 = plt.subplot(313)

labels = {'tempmax':'Maximum Temperature (\N{DEGREE SIGN}F)',
          'tempmin':'Minimum Temperature (\N{DEGREE SIGN}F)',
          'precip':'Precipitation (10x mm)',
          'precipprob': 'Precipitation Probability (%)',
          'cloudcover': 'Cloud Cover (%)',
          'solarradiation': 'Soldar Radiation (W/m$^2$)'}

def plotyears(ax, item, c='k', norm=1, alpha=0.3):
    alldays = np.array([x.split('-')[1]+x.split('-')[2] for x in data['datetime']])
    allplot = data[item]/norm
    plotmask = np.array([x not in plotdays for x in alldays])
    allplot_masked = np.ma.masked_where(plotmask, allplot)
    ax.plot(alldays, allplot_masked, c=c, alpha=alpha)

def prettyplot(ax, item, c='k', lw=3, norm=1, alpha=0.2, shadeerr=True, plottheyears=True):
    if item in labels.keys():
        label = labels[item]
    else:
        label = item
    ax.plot(days, avgdata[item]['avg']/norm, c=c, lw=lw, label=label)
    if shadeerr:
        ax.fill_between(days, avgdata[item]['std_l']/norm, avgdata[item]['std_u']/norm, color=c, alpha=alpha)
    if plottheyears:
        plotyears(ax, item, norm=norm, c=c)

### DO THE PLOTTING ###

prettyplot(ax1, 'tempmax', c='r')
prettyplot(ax1, 'tempmin', c='b')

prettyplot(ax2, 'precip', c='b', norm=0.00393701) # conver to 10*mm
prettyplot(ax2, 'precipprob', c='c')

prettyplot(ax3, 'cloudcover', c='grey')
prettyplot(ax3, 'solarradiation', c='tomato', norm=6)

### Pretty Plot ###

fontsize = 20
labelsize = fontsize-6

# set xticks
xticks = [x for x in days if x[-2:] in ['01', '15']]
months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
daylabels = [''] * len(xticks)
for i,xtick in enumerate(xticks):
    daylabels[i] = months[int(xtick[:2])] + ' ' + xtick[-2:]

for ax in [ax1, ax2, ax3]:
    ax.legend(fontsize=labelsize, loc=1)
    ax.set_xticks(xticks)
    ax.tick_params(axis='both', which='major', labelsize=labelsize)
    for xtick in xticks:
        ax.axvline(x=xtick, c='k', ls='--')
    if ax == ax3:
        ax.set_xticklabels(daylabels, rotation=45, fontsize=labelsize)
    else:
        ax.set_xticklabels([])
    ax.set_xlim([StartPlot, EndPlot])

ax1.set_ylim(30,90)
ax1.set_yticks([30,40,50,60,70,80,90])
ax2.set_ylim(0,100)
ax3.set_ylim(0,100)

# make title
startday = min(data['datetime']).split('-')[0]
endday = max(data['datetime']).split('-')[0]
city = re.sub(r"\B([A-Z])", r" \1", Location.split(',')[0])
ax1.set_title(f'Average Weather in {city} between {startday} and {endday}', fontsize=fontsize)

plt.tight_layout()
#plt.savefig(plotdir+f'Weather{Location}.png', bbox_inches='tight', dpi = 500)
plt.show()
