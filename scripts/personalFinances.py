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
import personalFinancesWrite as wrt
import personalFinancesPlot as plt

class MainApplication(tk.Frame):

    def __init__(self, master, *args, **kwargs):
        tk.Frame.__init__(self, master, *args, **kwargs)
        self.master = master
        master.title = 'Finance Tracker'
        self.path = os.path.dirname(os.path.dirname(__file__))
        self.ctime = datetime.now().strftime('%Y-%m-%d')
        os.chdir(self.path)

        ## Variable Initiation ##
        self.filename = 'data\personalFinancesData_test.json'
        os.remove('data\personalFinancesData_test.json')                                ## REMOVE THIS!! ##
        try: # Simply try to open datafile. Close it and continue.
            f = open(self.filename); f.close()
        except FileNotFoundError: # Initialize data file
            print('Building %s...' % self.filename)
            start_data = {
                'data': {'Date': ['2018-09-15', self.ctime], 'Elevations Checking': [000, 123]},
                'type': {'Date': ['Date'], 'Elevations Checking': ['type_test']},
                'subtype': {'Date': ['Date'], 'Elevations Checking': ['subtype_test']},
                'comment': {'Date': [None]}
            }
            with open(self.filename, "w") as write_file:
                json.dump(start_data, write_file)

        with open(self.filename, "r") as read_file:
            old_data = json.load(read_file)

        self.new_data = copy.deepcopy(old_data) # So that you don't overwrite stuff
        self.catagories = []
        for cat in self.new_data['data'].keys():
            self.catagories.append(cat)
        self.types = list(self.new_data['type'].keys())
        self.subtypes = list(self.new_data['subtype'].keys())

        self.entries = {}
        self.data = {}
        self.data_test = {}
        self.catName = {}
        self.catVal = {}

        self.typeChoices = np.unique(self.types).tolist()
        self.typeChoices.append('New')
        self.typeChoices.remove('Date')
        self.subtypeChoices = np.unique(self.subtypes).tolist()
        self.subtypeChoices.append('New')
        self.subtypeChoices.remove('Date')
        self.newType = tk.StringVar(root)
        self.newSubtype = tk.StringVar(root)
        self.typeChoser = tk.OptionMenu(master, self.newType, *self.typeChoices)
        self.subtypeChoser = tk.OptionMenu(master, self.newSubtype, *self.subtypeChoices)

        ## Add GUI Elements ##
        self.titleLabel = tk.Label(master, text='Finance Tracker')
        self.titleLabel.config(font=("Courier", 20))
        self.titleLabel.grid(row=0, column=0, columnspan=len(self.catagories), sticky=tk.W+tk.E)
        self.endLabel = tk.Label(master, text='Editing ' + self.filename + ' on ' + self.ctime)
        self.endLabel.grid(row=7, column=0, columnspan=len(self.catagories), sticky=tk.W+tk.E)

        self.val_numb = master.register(self.validateNumb) # we have to wrap the command
        self.val_date = master.register(self.validateDate) # we have to wrap the command
        for col,catagory in enumerate(self.catagories):
            self.catName[catagory] = tk.Label(master, text=catagory)
            self.catName[catagory].grid(row=1, column=col)
            if col == 0:
                self.data[catagory] = self.ctime
                self.catVal[catagory] = tk.Entry(master, validate="key", validatecommand=(self.val_date, '%P'), bg='green')
                self.catVal[catagory].insert(tk.END, self.ctime)
                self.catVal[catagory].grid(row=2, column=col)
                self.entries[catagory] = self.catVal[catagory]
            else:
                self.data[catagory] = 0
                self.catVal[catagory] = tk.Entry(master, validate="key", validatecommand=(self.val_numb, '%P'), bg='red')
                self.catVal[catagory].insert(tk.END, 0)
                self.catVal[catagory].grid(row=2, column=col)
                self.entries[catagory] = self.catVal[catagory]

        self.add_Data = tk.Button(master, text='Add new catagory.', command=lambda: self.addData())
        self.add_Data.grid(row=3, column=0, columnspan=len(self.catagories), sticky=tk.W+tk.E)

        self.write_Data = tk.Button(master, text='Write data to file.', command=lambda: self.writeData())
        self.write_Data.grid(row=4, column=0, columnspan=len(self.catagories), sticky=tk.W+tk.E)

        self.plot_Data = tk.Button(master, text='Show plot.', command=lambda: self.plotData())
        self.plot_Data.grid(row=6, column=0, columnspan=len(self.catagories), sticky=tk.W+tk.E)

    ''' other functions '''

    def validateDate(self, new_text):
        if not new_text: # the field is being cleared
            return False
        try:
            datetime.strptime(new_text, '%Y-%m-%d')
            return True
        except ValueError:
            return False

    def validateNumb(self, new_text):
        if not new_text: # the field is being cleared
            return False
        try:
            float(new_text) > 0
            return True
        except ValueError:
            return False

    def addData(self):
        self.add_Data.config(state='disabled')
        self.write_Data.config(state='disabled')
        self.plot_Data.config(state='disabled')
        self.newName = tk.Entry(self.master)
        self.newName.grid(row=1, column=len(self.catagories)+1)
        self.confirm = tk.Button(self.master, text='Confim.', command=lambda: self.confirmNew('catagory',self.newName.get()))
        self.confirm.grid(row=2, column=len(self.catagories)+1)

    def confirmNew(self, stage, catagory):
        if stage == 'catagory':
            self.newCat = self.newName.get()
            if self.newCat not in self.catagories:
                self.newName.grid_forget()
                self.catName[catagory] = tk.Label(self.master, text=' ' + self.newCat + ' ')
                self.catName[catagory].grid(row=1, column=len(self.catagories)+1)
                self.confirm.grid_forget()
                self.newType.set(self.typeChoices[0]) # set the default option
                self.typeChoser.grid(row=2, column=len(self.catagories)+1)
                self.confirm = tk.Button(self.master, text='Confim.', command=lambda: self.confirmNew('type', self.newCat))
                self.confirm.grid(row=3, column=len(self.catagories)+1)
        elif stage == 'type':
            self.types.append(self.newType.get())
            self.typeChoser.grid_forget()
            self.confirm.grid_forget()
            self.typeLabel = tk.Label(self.master, text=' ' + self.newType.get() + ' ')
            self.typeLabel.grid(row=2, column=len(self.catagories)+1)
            self.newSubtype.set(self.subtypeChoices[0]) # set the default option
            self.subtypeChoser.grid(row=3, column=len(self.catagories)+1)
            self.confirm = tk.Button(self.master, text='Confim.', command=lambda: self.confirmNew('subtype', self.newCat))
            self.confirm.grid(row=4, column=len(self.catagories)+1)
        elif stage == 'subtype':
            if self.newSubtype.get() == 'New':
                self.subtypeChoser.grid_forget()
                self.confirm.grid_forget()
                self.newSubtypeEntry = tk.Entry(self.master)
                self.newSubtypeEntry.grid(row=3, column=len(self.catagories)+1)
                self.confirm = tk.Button(self.master, text='Confim.', command=lambda: self.confirmNew('new_subtype', self.newCat))
                self.confirm.grid(row=4, column=len(self.catagories)+1)
            else:
                self.data[self.newCat] = 0
                self.catagories.append(self.newCat)
                self.subtypes.append(self.newSubtype.get())
                self.subtypeChoser.grid_forget()
                self.confirm.grid_forget()
                self.typeLabel.grid_forget()
                self.catVal[catagory] = tk.Entry(self.master, validate="key", validatecommand=(self.val_numb, '%P'), bg='red')
                self.catVal[catagory].grid(row=2, column=len(self.catagories))
                self.catVal[catagory].insert(tk.END, 0)
                self.entries[self.newCat] = self.catVal[catagory]
                self.add_Data.config(state='normal')
                self.add_Data.grid(columnspan=len(self.catagories)+1)
                self.write_Data.config(state='normal')
                self.write_Data.grid(columnspan=len(self.catagories)+1)
                self.plot_Data.config(state='normal')
                self.plot_Data.grid(columnspan=len(self.catagories)+1)
                self.titleLabel.grid(columnspan=len(self.catagories)+1)
                self.endLabel.grid(columnspan=len(self.catagories)+1)
        else: # if stage = new_subtype
            self.data[self.newCat] = 0
            self.catagories.append(self.newCat)
            self.subtypes.append(self.newSubtypeEntry.get())
            self.newSubtypeEntry.grid_forget()
            self.confirm.grid_forget()
            self.typeLabel.grid_forget()
            self.catVal[catagory] = tk.Entry(self.master, validate="key", validatecommand=(self.val_numb, '%P'), bg='red')
            self.catVal[catagory].grid(row=2, column=len(self.catagories))
            self.catVal[catagory].insert(tk.END, 0)
            self.entries[self.newCat] = self.catVal[catagory]
            self.add_Data.config(state='normal')
            self.add_Data.grid(columnspan=len(self.catagories)+1)
            self.write_Data.config(state='normal')
            self.write_Data.grid(columnspan=len(self.catagories)+1)
            self.plot_Data.config(state='normal')
            self.plot_Data.grid(columnspan=len(self.catagories)+1)
            self.titleLabel.grid(columnspan=len(self.catagories)+1)
            self.endLabel.grid(columnspan=len(self.catagories)+1)

    def writeData(self):
        # Reorganize GUI #
        for col,catagory in enumerate(self.catagories):
            self.catName[catagory].grid_forget()
            self.catVal[catagory].grid_forget()
        self.add_Data.grid_forget()
        self.write_Data.grid_forget()
        self.plot_Data.config(state='disabled')

        self.catConfirm = {}
        self.typConfirm = {}
        self.subConfirm = {}
        self.dataConfirm = {}

        for col,catagory in enumerate(self.catagories):
            if col == 0: # Make data list #
                self.data[catagory] = self.entries[catagory].get()
            else:
                self.data[catagory] = str(round(float(self.entries[catagory].get()),2))
            self.dataList = list(self.data.values())

            self.catConfirm[catagory] = tk.Label(self.master, text=''.join(self.catagories[col]))
            self.catConfirm[catagory].grid(row=1, column=col, columnspan=1, sticky=tk.W+tk.E)
            self.typConfirm[catagory] = tk.Label(self.master, text=''.join(self.types[col]))
            self.typConfirm[catagory].grid(row=2, column=col, columnspan=1, sticky=tk.W+tk.E)
            self.subConfirm[catagory] = tk.Label(self.master, text=''.join(self.subtypes[col]))
            self.subConfirm[catagory].grid(row=3, column=col, columnspan=1, sticky=tk.W+tk.E)
            self.dataConfirm[catagory] = tk.Label(self.master, text=''.join(self.dataList[col]))
            self.dataConfirm[catagory].grid(row=4, column=col, columnspan=1, sticky=tk.W+tk.E)

        self.confirm = tk.Button(self.master, text='Confim Data Entry.', command=lambda: self.confirmWrite())
        self.confirm.grid(row=5,column=0,columnspan=len(self.catagories), sticky=tk.W+tk.E)

    def confirmWrite(self):
        self.confirm.grid_forget()
        self.plot_Data.config(state='normal')

        # write data! #
        wrt.writeDataToFile(filename=self.filename,data=self.dataList,catagories=self.catagories,types=self.types,subtypes=self.subtypes)

    def plotData(self):
        plt.plotThedata(filename=self.filename)

if __name__ == "__main__":
    root = tk.Tk()
    MainApplication(root)
    root.mainloop()
