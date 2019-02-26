'''
Use Basemap to plot an interactive geo-tagged scrap book
'''

from mpl_toolkits.basemap import Basemap # needed pyproh, basemap and pillow + others?
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import matplotlib.image as mpimg
from datetime import datetime
import copy
import json
import os

class ZoomPlot():

    def __init__(self, pnts):
        self.fig = plt.figure(figsize=(15,9))
        self.ax = self.fig.add_subplot(111)

        self.days = pnts['days']
        self.lons = pnts['lons']
        self.lats = pnts['lats']
        self.dirs = pnts['dirs']
        self.coms = pnts['coms']

        self.bnds = self.bnds_strt = [-58, 80, -180, 180]
        self.resolution = 'c'

        # add callback for mouse clicks
        self.fig.canvas.mpl_connect('button_press_event', self.onclick)

        self.plot_map()

    def plot_map(self):
        self.map = Basemap(projection='merc',llcrnrlat=self.bnds[0],urcrnrlat=self.bnds[1],
                      llcrnrlon=self.bnds[2],urcrnrlon=self.bnds[3],resolution=self.resolution)

        self.map.drawcoastlines()
        self.map.drawmapboundary(fill_color='cornflowerblue')
        self.map.fillcontinents(color='lightgreen', lake_color='aqua')
        self.map.drawcountries()
        self.map.drawstates()

        self.plot_points()

        self.fig.canvas.draw()

        self.zoomcall = self.ax.callbacks.connect('ylim_changed', self.onzoom)

    def onzoom(self, axes):
        #print('zoom triggered')
        self.ax.patches.clear()
        self.ax.collections.clear()
        self.ax.callbacks.disconnect(self.zoomcall)

        x1, y1 = self.map(self.ax.get_xlim()[0], self.ax.get_ylim()[0], inverse = True)
        x2, y2 = self.map(self.ax.get_xlim()[1], self.ax.get_ylim()[1], inverse = True)
        self.bnds = [y1, y2, x1, x2]

        # reset zoom to home (workaround for unidentified error when you press the home button)
        if any([a/b > 1 for a,b in zip(self.bnds,self.bnds_strt)]):
            self.bnds = self.bnds_strt # reset map boundaryies
            self.ax.lines.clear() # reset points
            self.ab.set_visible(False) # hide picture if visible

        # change map resolution based on zoom level
        zoom_set = max(abs(self.bnds[0]-self.bnds[1]),abs(self.bnds[2]-self.bnds[3]))
        if zoom_set < 30 and zoom_set >= 3:
            self.resolution = 'l'
            #print('   --- low resolution')
        elif zoom_set < 3:
            self.resolution = 'i'
            #print('   --- intermeditate resolution')
        else:
            self.resolution = 'c'
            #print('   --- coarse resolution')

        self.plot_map()

    def plot_points(self):
        self.x, self.y = self.map(self.lons, self.lats)
        self.line, = self.map.plot(self.x, self.y, color='darkmagenta', linestyle='none', marker='o', markeredgecolor='gold')

        # create the annotations box
        self.pic = mpimg.imread('pics\\profpic.png') # just to set up variables, will change later
        self.im = OffsetImage(self.pic)
        self.xybox = (50., 50.)
        self.ab = AnnotationBbox(self.im, (0,0), xybox=self.xybox, xycoords='data',
                boxcoords="offset points",  pad=0.3,  arrowprops=dict(arrowstyle="->"))
        # add it to the axes and make it invisible
        self.ax.add_artist(self.ab)
        self.ab.set_visible(False)

    def onclick(self, event): # if you click on a data point
        if self.line.contains(event)[0]:
            # find out the index within the array from the event
            try:
                ind, = self.line.contains(event)[1]["ind"]
            except ValueError:
                print('Please zoom in!')
            else:
                # get the figure size
                w,h = self.fig.get_size_inches()*self.fig.dpi
                ws = (event.x > w/2.)*-1 + (event.x <= w/2.)
                hs = (event.y > h/2.)*-1 + (event.y <= h/2.)
                # if event occurs in the top or right quadrant of the figure,
                # change the annotation box position relative to mouse.
                self.ab.xybox = (self.xybox[0]*ws, self.xybox[1]*hs)
                # make annotation box visible
                self.ab.set_visible(True)
                # place it at the position of the hovered scatter point
                self.ab.xy = (self.x[ind], self.y[ind])
                # set the image corresponding to that point
                dir = self.dirs[ind]
                self.im.set_data(mpimg.imread(dir))
                # change zoom of the image to deal with different file sizes
                picsize = max(mpimg.imread(dir).shape)
                self.im.set_zoom(0.4*(1000/picsize)) # optimum: zoom = 0.4, picsize = 1000
        else:
            #if you didn't click on a data point
            self.ab.set_visible(False)
        self.fig.canvas.draw_idle()
