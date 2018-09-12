import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

def plotThedata(filename):
    '''
    ################################################################################
    #                                Get the Stuff                                 #
    ################################################################################
    '''

    path = os.path.dirname(__file__)
    file = open(path + '\\' + filename, 'r')
    catagories = file.readline().strip().split("\t")
    types = file.readline().strip().split("\t")
    subtypes = file.readline().strip().split("\t")

    allData = {}
    lists = {}
    sublists = {}
    for i,catagory in enumerate(catagories):
        allData[catagory] = []
        if types[i] not in lists.keys() and i is not 0:
            lists[types[i]] = []
        if subtypes[i] not in lists.keys() and i is not 0:
            sublists[subtypes[i]] = []

    for line in file:
        data = line.strip().split("\t")
        data = data + (len(catagories)-len(data)) * ['0']
        for i,catagory in enumerate(catagories):
            if i == 0:
                allData[catagory].append(datetime.strptime(data[i], '%Y-%m-%d'))
            else:
                allData[catagory].append(float(data[i].replace(',', '')))
    file.close()

    everything = []
    for i,catagory in enumerate(catagories):
        if i is not 0:
            everything.append(allData[catagory])
            lists[types[i]].append(allData[catagory])
            sublists[subtypes[i]].append(allData[catagory])

    totals = {}
    totals['types'] = {}
    totals['subtypes'] = {}
    for type in lists:
        totals['types'][type] = [sum(x) for x in zip(*lists[type])]
    for subtype in sublists:
        totals['subtypes'][subtype] = [sum(x) for x in zip(*sublists[subtype])]
    totals['total'] = [sum(x) for x in zip(*everything)]

    change = [x - y for x,y in zip(totals['total'][1:], totals['total'][:-1])]
    changePos = [x if x > 0 else 0 for x in change]
    changeNeg = [x if x <= 0 else 0 for x in change]

    '''
    ################################################################################
    #                                Plot the Stuff                                #
    ################################################################################
    '''

    plt.style.use('seaborn-white') # Set the style globally. See plotStyles.py for options
    plt.rcParams['font.family'] = 'DejaVu Sans'
    plt.rcParams['font.serif'] = 'Ubuntu'
    plt.rcParams['font.monospace'] = 'Ubuntu Mono'
    plt.rcParams['font.size'] = 10
    plt.rcParams['axes.labelsize'] = 10
    plt.rcParams['axes.titlesize'] = 12
    plt.rcParams['xtick.labelsize'] = 8
    plt.rcParams['ytick.labelsize'] = 8
    plt.rcParams['legend.fontsize'] = 10
    plt.rcParams['figure.titlesize'] = 18

    width, height = plt.figaspect(.52) # Set an aspect ratio
    fig = plt.figure(figsize=(width,height), dpi=120)

    ## Main Overview Plot ##
    ax1 = plt.subplot(2,3,(1,5))
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax1.xaxis.set_major_locator(mdates.YearLocator())

    plt.plot(allData['Month'], totals['total'], label='Total', linewidth=3, color='k') # total first in legend
    colormap = plt.cm.tab10
    colors = [colormap(i) for i in np.linspace(0, 1, 10)]
    for i,type in enumerate(totals['types'].keys()): # plot types
        plt.plot(allData['Month'], totals['types'][type], label=type, linewidth=3, color=colors[i])
    colormap = plt.cm.Pastel1
    colors = [colormap(i) for i in np.linspace(0, 1, 9)]
    for i,subtype in enumerate(totals['subtypes'].keys()): # plot subtypes
        plt.plot(allData['Month'], totals['subtypes'][subtype], label=subtype, linewidth=2, linestyle='--', color=colors[i])
    plt.plot(allData['Month'], totals['total'], linewidth=3, color='k') # to plot on top

    plt.xlim(allData['Month'][0])
    plt.ylim(0, 1.1*max(totals['total']))
    plt.xlabel('Time')
    plt.ylabel('Savings (Dollars)')
    ax1.set_title('Overview', fontweight='bold')
    plt.legend(loc=2)

    ## Change from Previous Month ##
    ax2 = plt.subplot(2,3,3)
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax2.xaxis.set_major_locator(mdates.YearLocator())

    plt.bar(allData['Month'][1:], changePos, 25, color='g')
    plt.bar(allData['Month'][1:], changeNeg, 25, color='r')
    plt.axhline(y=0, linestyle='-', linewidth=0.5, color='k')

    plt.xlim(allData['Month'][0])
    plt.xlabel('Time')
    plt.ylabel('Change (Dollars)')
    ax2.set_title('Change from Previous Month', fontweight='bold')

    ## Last Six Months ##
    ax3 = plt.subplot(2,3,6)
    ax3.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
    ax3.xaxis.set_major_locator(mdates.MonthLocator())

    plt.plot(allData['Month'][-6:], totals['total'][-6:], label='Total', linewidth=3)

    plt.xlabel('Time')
    plt.ylabel('Savings (Dollars)')
    plt.text(0.05, 0.9, 'Net Change = $' + '%.2f'%float(totals['total'][-1]-totals['total'][-6]), ha='left', va='center', transform=ax3.transAxes)
    ax3.set_title('Last Six Months', fontweight='bold')

    ax4 = ax3.twinx()
    ax4.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
    ax4.xaxis.set_major_locator(mdates.MonthLocator())

    plt.bar(allData['Month'][-6:], changePos[-6:], 25, alpha=0.5, color='g')
    plt.bar(allData['Month'][-6:], changeNeg[-6:], 25, alpha=0.5, color='r')
    plt.axhline(y=0, linestyle='-', linewidth=0.5, color='k')

    plt.ylim(1.5*min(changeNeg[-6:]),1.5*max(changePos[-6:]))
    ax4.get_yaxis().set_visible(False)

    #plt.subplots_adjust(left=0.15, bottom=None, right=0.95, top=None, hspace=0.4, wspace=0.40)
    plt.tight_layout()
    plt.savefig(path + '\\PersonalFinances.png', bbox_inches='tight', dpi = 500)
    plt.show()
