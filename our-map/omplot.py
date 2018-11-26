'''
Use Basemap to plot an interactive geo-tagged scrap book
'''

def makeamap(filename):
    from mpl_toolkits.basemap import Basemap # needed pyproh, basemap and pillow + others?
    import numpy as np
    import matplotlib.pyplot as plt
    from matplotlib.offsetbox import OffsetImage, AnnotationBbox
    import matplotlib.image as mpimg
    from datetime import datetime
    import copy
    import json
    import os

    ''' SETUP THE MAP '''
    # create new figure, axes instances
    fig = plt.figure(dpi=150)
    ax = fig.add_axes([0.1,0.1,0.8,0.8])
    # setup mercator map projection
    map = Basemap(projection='merc',llcrnrlat=-58,urcrnrlat=80,
                llcrnrlon=-180,urcrnrlon=180,resolution='c')

    ''' GET THE DATA '''
    with open(filename, "r") as read_file: #### THIS IS HOW YOU READ ####
        data = json.load(read_file)

    days = []
    lons = []
    lats = []
    dirs = []
    coms = []
    for name in data.keys():
        days.append(data[name]['day'])
        lons.append(data[name]['lon'])
        lats.append(data[name]['lat'])
        dirs.append(data[name]['dir'])
        coms.append(data[name]['com'])

    x,y = map(lons, lats)
    line, = map.plot(x, y, 'bo')

    ''' DRAW THE MAP '''
    map.drawcoastlines(linewidth=0.50)
    map.fillcontinents()
    map.drawmapboundary()
    map.drawcountries()

    # create the annotations box
    pic = mpimg.imread('pics\\profpic.png') # just to set up variables, will change later
    im = OffsetImage(pic)
    xybox=(50., 50.)
    ab = AnnotationBbox(im, (0,0), xybox=xybox, xycoords='data',
            boxcoords="offset points",  pad=0.3,  arrowprops=dict(arrowstyle="->"))
    # add it to the axes and make it invisible
    ax.add_artist(ab)
    ab.set_visible(False)

    # Declare and register callbacks for zoom control
    def on_lims_change(axes):
        xrange = abs(ax.get_xlim()[1] - ax.get_xlim()[0])
        yrange = abs(ax.get_xlim()[1] - ax.get_xlim()[0])
        print('max range: {}'.format(max(xrange,yrange)))
        if max(xrange,yrange) < 1E7 and max(xrange,yrange) > 1E6: # 'l' = low
            map.resolution = 'l'
            map.drawstates()
        elif max(xrange,yrange) < 1E6 and max(xrange,yrange) > 5E5: # 'i' = intermeditate
            map.resolution = 'i'
            map.drawstates()
        elif max(xrange,yrange) < 5E5 and max(xrange,yrange) > 1E5: # 'h' = high
            map.resolution = 'h'
            map.drawstates()
        elif max(xrange,yrange) < 1E5: # 'f' = full
            map.resolution = 'f'
            map.drawstates()
        else: # 'c' = coarse
            map.resolution = 'c'
        print(map.resolution)
        map.drawcoastlines(linewidth=0.50)
        map.fillcontinents()
        map.drawmapboundary()

    ax.callbacks.connect('xlim_changed', on_lims_change)
    #ax.callbacks.connect('ylim_changed', on_lims_change)

    def onclick(event): # if you click on a data point
        if line.contains(event)[0]:
            # find out the index within the array from the event
            try:
                ind, = line.contains(event)[1]["ind"]
            except ValueError:
                print('Please zoom in!')
            else:
                # get the figure size
                w,h = fig.get_size_inches()*fig.dpi
                ws = (event.x > w/2.)*-1 + (event.x <= w/2.)
                hs = (event.y > h/2.)*-1 + (event.y <= h/2.)
                # if event occurs in the top or right quadrant of the figure,
                # change the annotation box position relative to mouse.
                ab.xybox = (xybox[0]*ws, xybox[1]*hs)
                # make annotation box visible
                ab.set_visible(True)
                # place it at the position of the hovered scatter point
                ab.xy = (x[ind], y[ind])
                # set the image corresponding to that point
                dir = dirs[ind]
                im.set_data(mpimg.imread(dir))
                # change zoom of the image to deal with different file sizes
                picsize = max(mpimg.imread(dir).shape)
                im.set_zoom(0.2*(1000/picsize)) # optimum: zoom = 0.2, picsize = 1000
        else:
            #if you didn't click on a data point
            ab.set_visible(False)
        fig.canvas.draw_idle()

    # add callback for mouse clicks
    fig.canvas.mpl_connect('button_press_event', onclick)

    plt.show()
