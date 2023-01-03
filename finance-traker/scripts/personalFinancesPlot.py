import os
import json
import copy
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta

def plotThedata(filename):
    '''
    ################################################################################
    #                                Get the Stuff                                 #
    ################################################################################
    '''

    path = os.path.dirname(os.path.dirname(__file__))
    with open(filename, "r") as read_file:
        read_data = json.load(read_file)
    data = copy.copy(read_data)

    time = [datetime.strptime(date, '%Y-%m-%d') for date in data['data']['Date']]
    types = [data['type'][cat] for cat in data['data'].keys() if cat != 'Date']
    subtypes = [data['subtype'][cat] for cat in data['data'].keys() if cat != 'Date']
    comments = data['comment']

    # if the subtype is "Joint", divide the data by two
    for cat in data['data'].keys():
        if data['subtype'][cat] == 'Joint':
            data['data'][cat] = [x * 0.5 for x in data['data'][cat]]

    totals = {}
    totals['types'] = {}
    totals['subtypes'] = {}
    for type in np.unique(types).tolist():
        sel = [data['data'][cat] for cat in data['data'].keys() if data['type'][cat] == type]
        totals['types'][type] = [sum(x) for x in zip(*sel)]
    for subtype in np.unique(subtypes).tolist():
        sel = [data['data'][cat] for cat in data['data'].keys() if data['subtype'][cat] == subtype]
        totals['subtypes'][subtype] = [sum(x) for x in zip(*sel)]
    totals['total'] = [sum(x) for x in zip(*[data['data'][cat] for cat in data['data'].keys() if cat != 'Date'])]

    if len(time) < 7: # not enough times yet
        for type in np.unique(types).tolist():
            totals['types'][type] = [0]*(7-len(time)) + totals['types'][type] # buffer with zeros
        for subtype in np.unique(subtypes).tolist():
            totals['subtypes'][subtype] = [0]*(7-len(time)) + totals['subtypes'][subtype] # buffer with zeros
        totals['total'] = [0]*(7-len(time)) + totals['total'] # buffer with zeros
        comments = [None]*(7-len(time)) + comments # buffer with zeros
        while len(time) < 7: # change time last
            time = [time[0]-timedelta(days=1)] + time

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

    plt.plot(time, totals['total'], label='Total', linewidth=3, color='k') # total first in legend
    colormap = plt.cm.tab10
    colors = [colormap(i) for i in np.linspace(0, 1, 10)]
    for i,type in enumerate(totals['types'].keys()): # plot types
        plt.plot(time, totals['types'][type], label=type, linewidth=3, color=colors[i])
    colormap = plt.cm.Pastel1
    colors = [colormap(i) for i in np.linspace(0, 1, 9)]
    for i,subtype in enumerate(totals['subtypes'].keys()): # plot subtypes
        plt.plot(time, totals['subtypes'][subtype], label=subtype, linewidth=2, linestyle='--', color=colors[i])
    line, = ax1.plot(time, totals['total'], linewidth=3, color='k') # to plot on top; for interactive

    plt.xlim(time[0])
    plt.ylim(0, 1.1*max(totals['total']))
    plt.xlabel('Time')
    plt.ylabel('Savings (Dollars)')
    ax1.set_title('Overview', fontweight='bold')
    plt.legend(loc=2)

    ## Change from Previous Month ##
    ax2 = plt.subplot(2,3,3)
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax2.xaxis.set_major_locator(mdates.YearLocator())

    plt.bar(time[1:], changePos, (mdates.date2num(time[-1])-mdates.date2num(time[1]))/len(changePos), color='g')
    plt.bar(time[1:], changeNeg, (mdates.date2num(time[-1])-mdates.date2num(time[1]))/len(changePos), color='r')
    plt.axhline(y=0, linestyle='-', linewidth=0.5, color='k')

    plt.xlim(time[0])
    plt.xlabel('Time')
    plt.ylabel('Change (Dollars)')
    ax2.set_title('Change from Previous Month', fontweight='bold')

    ## Last Six Months ##
    ax3 = plt.subplot(2,3,6)
    ax3.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
    ax3.xaxis.set_major_locator(mdates.MonthLocator())

    plt.plot(time[-6:], totals['total'][-6:], label='Total', linewidth=3)

    plt.xlabel('Time')
    plt.ylabel('Savings (Dollars)')
    plt.text(0.05, 0.9, 'Net Change = $' + '%.2f'%float(totals['total'][-1]-totals['total'][-6]), ha='left', va='center', transform=ax3.transAxes)
    ax3.set_ylim(0.7*min(totals['total'][-6:]),1.3*max(totals['total'][-6:]))
    ax3.set_title('Last Six Months', fontweight='bold')

    ax4 = ax3.twinx()
    ax4.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
    ax4.xaxis.set_major_locator(mdates.MonthLocator())

    plt.bar(time[-6:], changePos[-6:], (mdates.date2num(time[-1])-mdates.date2num(time[-6]))/6, alpha=0.5, color='g')
    plt.bar(time[-6:], changeNeg[-6:], (mdates.date2num(time[-1])-mdates.date2num(time[-6]))/6, alpha=0.5, color='r')
    ax4.set_ylim(1.3*min(changeNeg[-6:]),1.3*max(changePos[-6:]))
    plt.axhline(y=0, linestyle='-', linewidth=0.5, color='k')
    ax4.get_yaxis().set_visible(False)

    #plt.subplots_adjust(left=0.15, bottom=None, right=0.95, top=None, hspace=0.4, wspace=0.40)
    plt.tight_layout()
    plt.savefig(path + '/PersonalFinances.png', bbox_inches='tight', dpi = 500)

    ## THE INTERACTIVE STUFF ##
    def replace_right(source, target, replacement, replacements=None):
        return replacement.join(source.rsplit(target, replacements))

    def onclick(event):
        for txt in ax1.texts: # clean up
            txt.remove()
        if event.inaxes!=line.axes: return # make sure you clicked in the main plot
        ind = np.argmin([abs(mdates.date2num(t)-event.xdata) for t in time])
        comment = ''
        maxind = 33
        try: # cut the string at spaces so that it fits on the graph
            s2 = comments[ind]
            while len(s2) > maxind:
                s1 = replace_right(s2[:maxind],' ','\n',1)
                cut = s1.index('\n') + 1
                comment += s1[:cut]
                s2 = '  ' + s2[cut:]
            comment += s2
        except TypeError: # object of type 'NoneType' has no len()
            comment += 'No comment...'
        textvar = ax1.text(0.3,0.98,'{}: {}'.format(time[ind].strftime('%Y-%m-%d'),comment), ha='left',va='top', transform=ax1.transAxes)
        plt.draw()

    fig.canvas.mpl_connect('button_press_event', onclick)

    plt.show()
