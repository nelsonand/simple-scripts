'''
################################################################################
#                            Script for Master GUI                             #
################################################################################
'''

import os
import json
import copy
import numpy as np
from datetime import datetime
import tkinter as tk
from tkinter import ttk
from omplot import makeamap

class MainApplication(ttk.Frame):

    def __init__(self, master, *args, **kwargs):
        ttk.Frame.__init__(self, master, *args, **kwargs)
        self.master = master
        master.title("Our Map")
        master.resizable(False,False)
        self.path = os.path.dirname(os.path.dirname(__file__))
        self.ctime = datetime.now().strftime('%Y-%m-%d')
        os.chdir(self.path+'\our-map')

        # fill in blank spaces
        self.maxcol = 6
        self.filler = ttk.Label(master, text='')
        self.filler.grid(row=0, column=0, rowspan=100, columnspan=self.maxcol, sticky=tk.W+tk.E+tk.S+tk.N+tk.S+tk.N)

        ## Initiate Datafile ##
        self.filename = 'omdata.json'
        try: # Simply try to open datafile. Close it and continue.
            f = open(self.filename); f.close()
        except FileNotFoundError: # Initialize data file
            print('Building %s...' % self.filename)
            start_data = {'name1':{
                                    'day':datetime.now().strftime('%Y-%m-%d'),
                                    'lat':57.0799,
                                    'lon':-135.3318,
                                    'dir':'pics\LOVEBar2.png',
                                    'com':'This is a comment.',
                                  }
                         }
            with open(self.filename, "w") as write_file:
                json.dump(start_data, write_file)

        ## Get Data ##
        with open(self.filename, "r") as read_file:
            old_data = json.load(read_file)

        ## Setup Variables ##
        self.data = copy.deepcopy(old_data) # just in case
        self.nams = []
        self.days = []
        self.lons = []
        self.lats = []
        self.dirs = []
        self.coms = []
        for name in self.data.keys():
            self.nams.append(name)
            self.days.append(self.data[name]['day'])
            self.lons.append(self.data[name]['lon'])
            self.lats.append(self.data[name]['lat'])
            self.dirs.append(self.data[name]['dir'])
            self.coms.append(self.data[name]['com'])

        ## Add GUI Elements ##
        self.titleLabel = ttk.Label(master, text='Our Map', width=50) # this width sets the starting GUI width
        self.titleLabel.config(font=('Courier', 20, 'bold'))
        self.titleLabel.grid(row=0, column=0, columnspan=self.maxcol, sticky=tk.W+tk.E+tk.S+tk.N)
        self.endLabel = ttk.Label(master, text='Editing ' + self.filename + ' on ' + self.ctime)
        self.endLabel.grid(row=100, column=0, columnspan=self.maxcol, sticky=tk.W+tk.E+tk.S+tk.N)

        # validation scripts (we have to wrap the command)
        self.val_name = master.register(self.validateName)
        self.val_numb = master.register(self.validateNumb)
        self.val_date = master.register(self.validateDate)

        # add the buttons
        self.add_Data = ttk.Button(master, text='Add Data', command=lambda: self.workData('add'))
        self.edit_Data= ttk.Button(master, text='Edit Data', command=lambda:self.workData('edit'))
        self.plot_Data = ttk.Button(master, text='Show the Map!', command=lambda: self.plotData())
        self.add_Data.grid(row=50, column=0, columnspan=self.maxcol, sticky=tk.W+tk.E+tk.S+tk.N)
        self.edit_Data.grid(row=60, column=0, columnspan=self.maxcol, sticky=tk.W+tk.E+tk.S+tk.N)
        self.plot_Data.grid(row=99, column=0, columnspan=self.maxcol, sticky=tk.W+tk.E+tk.S+tk.N)

        # elements for later (just toggle visibility)
        self.namLabel = ttk.Label(master, text='Name')
        self.dayLabel = ttk.Label(master, text='Day')
        self.lonLabel = ttk.Label(master, text='Longitude')
        self.latLabel = ttk.Label(master, text='Latitude')
        self.dirLabel = ttk.Label(master, text='Photo Directory')
        self.comLabel = ttk.Label(master, text='Comment (optional)')
        self.namEntry = ttk.Entry(master, validate="key", validatecommand=(self.val_name, '%P'))
        self.dayEntry = ttk.Entry(master, validate="key")#, validatecommand=(self.val_date, '%P'))
        self.lonEntry = ttk.Entry(master, validate="key", validatecommand=(self.val_numb, '%P'))
        self.latEntry = ttk.Entry(master, validate="key", validatecommand=(self.val_numb, '%P'))
        self.dirEntry = ttk.Entry(master, validate="key")
        self.comEntry = ttk.Entry(master, validate="key")

        self.work_Data_confirm = ttk.Button(master, text='Confirm', command=lambda: self.workData_confirm())

        # I don't want to do this every time but am not sure how they are set and want to reset the Choser TODO
        self.editName = tk.StringVar(root)
        self.editName_Choices = ['Select Entry'] + self.nams[::-1] # reversed
        self.editName_Choser = ttk.OptionMenu(self.master, self.editName, *self.editName_Choices, command=self.update_editName)

    ## The function definitions ##
    def validateName(self, new_text): # Name valification TODO
        return True

    def validateDate(self, new_text): # date valification
        if not new_text: # the field is being cleared
            return False
        try:
            datetime.strptime(new_text, '%Y-%m-%d')
            return True
        except ValueError:
            return False

    def validateNumb(self, new_text): # number valification
        if not new_text: # the field is being cleared
            return True
        try:
            float(new_text)
            return True
        except ValueError:
            if new_text == '-':
                return True
            else:
                return False

    def workData(self, type): # set up the input GUI
        if type == 'add':
            baserow = 50
            self.namEntry.grid(row=baserow+2, column=0, columnspan=1, sticky=tk.W+tk.E+tk.S+tk.N)
        elif type == 'edit': # a few more commands for selecting a date to edit
            baserow = 60
            self.editName = tk.StringVar(root)
            self.editName_Choices = ['Select Entry'] + self.nams[::-1] # reversed
            self.editName_Choser = ttk.OptionMenu(self.master, self.editName, *self.editName_Choices, command=self.update_editName)
            self.editName_Choser.grid(row=baserow+2, column=0, columnspan=1, sticky=tk.W+tk.E+tk.S+tk.N)
            self.dayEntry.config(state='disabled')
            self.lonEntry.config(state='disabled')
            self.latEntry.config(state='disabled')
            self.dirEntry.config(state='disabled')
            self.comEntry.config(state='disabled')
            self.work_Data_confirm.config(state='disabled')

        self.add_Data.config(state='disabled')
        self.edit_Data.config(state='disabled')
        self.plot_Data.config(state='disabled')
        self.namLabel.grid(row=baserow+1, column=0, columnspan=1, sticky=tk.W+tk.E+tk.S+tk.N)
        self.dayLabel.grid(row=baserow+1, column=1, columnspan=1, sticky=tk.W+tk.E+tk.S+tk.N)
        self.lonLabel.grid(row=baserow+1, column=2, columnspan=1, sticky=tk.W+tk.E+tk.S+tk.N)
        self.latLabel.grid(row=baserow+1, column=3, columnspan=1, sticky=tk.W+tk.E+tk.S+tk.N)
        self.dirLabel.grid(row=baserow+1, column=4, columnspan=1, sticky=tk.W+tk.E+tk.S+tk.N)
        self.comLabel.grid(row=baserow+1, column=5, columnspan=1, sticky=tk.W+tk.E+tk.S+tk.N)
        self.dayEntry.grid(row=baserow+2, column=1, columnspan=1, sticky=tk.W+tk.E+tk.S+tk.N)
        self.lonEntry.grid(row=baserow+2, column=2, columnspan=1, sticky=tk.W+tk.E+tk.S+tk.N)
        self.latEntry.grid(row=baserow+2, column=3, columnspan=1, sticky=tk.W+tk.E+tk.S+tk.N)
        self.dirEntry.grid(row=baserow+2, column=4, columnspan=1, sticky=tk.W+tk.E+tk.S+tk.N)
        self.comEntry.grid(row=baserow+2, column=5, columnspan=1, sticky=tk.W+tk.E+tk.S+tk.N)
        self.work_Data_confirm.grid(row=baserow+3, column=0, columnspan=self.maxcol, sticky=tk.W+tk.E+tk.S+tk.N)

        self.namEntry.insert(tk.END, 'TEST')
        self.dayEntry.insert(tk.END, '10-10-10')
        self.lonEntry.insert(tk.END, '1')
        self.latEntry.insert(tk.END, '0')
        self.dirEntry.insert(tk.END, 'test')
        self.comEntry.insert(tk.END, 'test')

    def workData_confirm(self): # save new data and clean up GUI
        # clean up GUI
        self.add_Data.config(state='normal')
        self.edit_Data.config(state='normal')
        self.plot_Data.config(state='normal')
        self.namLabel.grid_forget()
        self.dayLabel.grid_forget()
        self.lonLabel.grid_forget()
        self.latLabel.grid_forget()
        self.dirLabel.grid_forget()
        self.comLabel.grid_forget()
        self.namEntry.grid_forget()
        self.dayEntry.grid_forget()
        self.editName_Choser.grid_forget()
        self.lonEntry.grid_forget()
        self.latEntry.grid_forget()
        self.dirEntry.grid_forget()
        self.comEntry.grid_forget()
        self.work_Data_confirm.grid_forget()

        # save new data
        nam = self.namEntry.get()
        day = self.dayEntry.get()
        lon = self.lonEntry.get()
        lat = self.latEntry.get()
        dir = self.dirEntry.get()
        com = self.comEntry.get()
        print(day,lon,lat,dir,com)
        print('ACTUALLY DO SOMETHIGN WITH THE DATA') # TODO
        # load data
        # if ___: # if name exists already then replace that entry
        # else: # add a new entry

        # clean entries
        self.namEntry.delete(0,tk.END)
        self.dayEntry.delete(0,tk.END)
        self.lonEntry.delete(0,tk.END)
        self.latEntry.delete(0,tk.END)
        self.dirEntry.delete(0,tk.END)
        self.comEntry.delete(0,tk.END)

    def update_editName(self,value):
        # enable entries to continue workflow
        self.dayEntry.config(state='normal')
        self.lonEntry.config(state='normal')
        self.latEntry.config(state='normal')
        self.dirEntry.config(state='normal')
        self.comEntry.config(state='normal')
        self.work_Data_confirm.config(state='normal')

        # edit day entry for consistent data storage
        self.namEntry.delete(0,tk.END)
        self.namEntry.insert(tk.END, value)

        print('update edit {}'.format(value))
        print('ACTUALLY DO SOMETHIGN WITH THE DATA') # TODO

    def plotData(self):
        makeamap(self.filename)

root = tk.Tk()
root.style = ttk.Style()
root.style.theme_use('vista') # 'winnative', 'clam', 'alt', 'default', 'classic', 'vista', 'xpnative'
root.style.configure('TLabel', background = '#87CEEB', anchor='center')
root.style.configure('TButton', background = 'gold1')
MainApplication(root)
root.mainloop()
