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
import personalFinancesWrite as wrt
import personalFinancesPlot as plt

class MainApplication(ttk.Frame):

    def __init__(self, master, *args, **kwargs):
        ttk.Frame.__init__(self, master, *args, **kwargs)
        self.master = master
        master.resizable(False,False)
        master.title("Oak's Finance Tracker")
        self.path = os.path.dirname(os.path.dirname(__file__))
        self.ctime = datetime.now().strftime('%Y-%m-%d')
        os.chdir(self.path)
        self.maxcol = 6
        # fill in blank spaces
        self.filler = ttk.Label(master, text='')
        self.filler.grid(row=0, column=0, rowspan=100, columnspan=self.maxcol, sticky=tk.W+tk.E+tk.S+tk.N+tk.S+tk.N)

        ## Initiate Datafile ##
        self.filename = 'data/personalFinancesData.json'
        try: # Simply try to open datafile. Close it and continue.
            f = open(self.filename); f.close()
        except FileNotFoundError: # Initialize data file
            print('Building %s...' % self.filename)
            start_data = {
                'data': {'Date': []},
                'type': {'Date': 'Date'},
                'subtype': {'Date': 'Date'},
                'comment': []
            }
            with open(self.filename, "w") as write_file:
                json.dump(start_data, write_file)

        ## Get Data ##
        with open(self.filename, "r") as read_file:
            old_data = json.load(read_file)

        ## Setup Variables ##
        self.cur_data = copy.deepcopy(old_data) # So that you don't overwrite stuff
        self.catagories = []
        self.types = []
        self.subtypes = []
        for cat in self.cur_data['data'].keys():
            self.catagories.append(cat)
            self.types.append(self.cur_data['type'][cat])
            self.subtypes.append(self.cur_data['subtype'][cat])
        # comments are organized by date
        self.comments = self.cur_data['comment'] + [None]
        self.dates = self.cur_data['data']['Date'] + ['Today']

        self.entries = {}
        self.data = {}
        self.catName = {}
        self.catVal = {}

        ## Add GUI Elements ##
        self.titleLabel = ttk.Label(master, text='Finance Tracker',width=10*self.maxcol)
        self.titleLabel.config(font=('Courier', 20, 'bold'))
        self.titleLabel.grid(row=0, column=0, columnspan=self.maxcol, sticky=tk.W+tk.E+tk.S+tk.N)
        self.endLabel = ttk.Label(master, text='Editing ' + self.filename + ' on ' + self.ctime)
        self.endLabel.grid(row=100, column=0, columnspan=self.maxcol, sticky=tk.W+tk.E+tk.S+tk.N)

        self.newrow = 0 # for grid making
        self.val_numb = master.register(self.validateNumb) # we have to wrap the command
        self.val_date = master.register(self.validateDate) # we have to wrap the command
        for ind,cat in enumerate(self.catagories):
            if ind == 0:
                col = ind
                self.catName[cat] = ttk.Label(master, text=cat)
                self.catName[cat].grid(row=1, column=col, sticky=tk.W+tk.E+tk.S+tk.N)
                self.data[cat] = self.ctime
                self.catVal[cat] = ttk.Entry(master, validate="key", validatecommand=(self.val_date, '%P'))
                self.catVal[cat].insert(tk.END, self.ctime)
                self.catVal[cat].grid(row=2, column=col)
                self.entries[cat] = self.catVal[cat]
            else:
                if (ind+1*round(self.newrow/2))%self.maxcol == 0:
                    self.newrow += 2
                if self.newrow == 0:
                    col = (ind+1*round(self.newrow/2)) - round(self.maxcol*self.newrow/2)
                else:
                    col = (ind+1*round(self.newrow/2)) - round(self.maxcol*self.newrow/2)
                    if col == -1:
                        col = self.maxcol - 1
                self.catName[cat] = ttk.Label(master, text=cat)
                self.catName[cat].grid(row=1+self.newrow, column=col, sticky=tk.W+tk.E+tk.S+tk.N)
                self.data[cat] = 0
                self.catVal[cat] = ttk.Entry(master, validate="key", validatecommand=(self.val_numb, '%P'))
                self.catVal[cat].insert(tk.END, 0)
                self.catVal[cat].grid(row=2+self.newrow, column=col)
                self.entries[cat] = self.catVal[cat]

        # add the buttons
        self.add_Data = ttk.Button(master, text='Add new catagory', command=lambda: self.addData())
        self.add_Data.grid(row=63, column=0, columnspan=self.maxcol, sticky=tk.W+tk.E+tk.S+tk.N)

        self.add_Comment = ttk.Button(master, text='Add comment', command=lambda:self.addComment())
        self.add_Comment.grid(row=64, column=0, columnspan=self.maxcol, sticky=tk.W+tk.E+tk.S+tk.N)

        self.new_Comment = ttk.Entry(self.master)

        self.write_Data = ttk.Button(master, text='Write data to file', command=lambda: self.writeData())
        self.write_Data.grid(row=65, column=0, columnspan=self.maxcol, sticky=tk.W+tk.E+tk.S+tk.N)

        self.plot_Data = ttk.Button(master, text='Show plot', command=lambda: self.plotData())
        self.plot_Data.grid(row=99, column=0, columnspan=self.maxcol, sticky=tk.W+tk.E+tk.S+tk.N)

        self.new_Comment = ttk.Entry(self.master)
        self.confirm_Comment = ttk.Button(self.master, text='Save comment', command=lambda: self.saveComment())

        ## Setup Type/Subtype Options ##
        self.typeChoices = ['Solid','Liquid']
        self.subtypeChoices = np.unique(self.subtypes).tolist()
        self.subtypeChoices.append('New')
        self.subtypeChoices.remove('Date')
        self.newType = tk.StringVar(root)
        self.newSubtype = tk.StringVar(root)
        self.typeChoser = ttk.OptionMenu(master, self.newType, self.typeChoices[0], *self.typeChoices)
        self.subtypeChoser = ttk.OptionMenu(master, self.newSubtype, self.subtypeChoices[0], *self.subtypeChoices)
        self.dateChoices = ['Select Date'] + self.dates[::-1] # reversed
        self.commentDate = tk.StringVar(root)
        self.dateChoser = ttk.OptionMenu(master, self.commentDate, *self.dateChoices, command=self.updateComment)

    ''' ------------------------------- other functions ------------------------------- '''

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
            return True
        try:
            float(new_text) > 0
            return True
        except ValueError:
            return False

    def addData(self):
        self.add_Data.config(state='disabled')
        self.add_Comment.config(state='disabled')
        self.write_Data.config(state='disabled')
        self.plot_Data.config(state='disabled')
        self.newNameLabel = tk.Label(self.master, text='Name:')
        self.newNameLabel.grid(row=1, column=self.maxcol+1)
        self.newName = ttk.Entry(self.master)
        self.newName.grid(row=1, column=self.maxcol+2)
        self.confirm = ttk.Button(self.master, text='Confim.', command=lambda: self.confirmNew('catagory',self.newName.get()))
        self.confirm.grid(row=2, column=self.maxcol+2)

    def confirmNew(self, stage, catagory):
        if stage == 'catagory':
            self.newCat = self.newName.get()
            if self.newCat not in self.catagories:
                self.newName.grid_forget()
                self.newTypeLabel = tk.Label(self.master, text='Type:')
                self.newTypeLabel.grid(row=2, column=self.maxcol+1)
                self.catName[catagory] = ttk.Label(self.master, text=' ' + self.newCat + ' ')
                self.catName[catagory].grid(row=1, column=self.maxcol+2, sticky=tk.W+tk.E+tk.S+tk.N)
                self.confirm.grid_forget()
                self.newType.set(self.typeChoices[0]) # set the default option
                self.typeChoser.grid(row=2, column=self.maxcol+2)
                self.confirm = ttk.Button(self.master, text='Confim.', command=lambda: self.confirmNew('type', self.newCat))
                self.confirm.grid(row=3, column=self.maxcol+2)
        elif stage == 'type':
            self.types.append(self.newType.get())
            self.typeChoser.grid_forget()
            self.confirm.grid_forget()
            self.newSubtypeLabel = tk.Label(self.master, text='Subtype:')
            self.newSubtypeLabel.grid(row=3, column=self.maxcol+1)
            self.typeLabel = ttk.Label(self.master, text=' ' + self.newType.get() + ' ')
            self.typeLabel.grid(row=2, column=self.maxcol+2, sticky=tk.W+tk.E+tk.S+tk.N)
            self.newSubtype.set(self.subtypeChoices[0]) # set the default option
            self.subtypeChoser.grid(row=3, column=self.maxcol+2)
            self.confirm = ttk.Button(self.master, text='Confim.', command=lambda: self.confirmNew('subtype', self.newCat))
            self.confirm.grid(row=4, column=self.maxcol+2)
        elif stage == 'subtype':
            if self.newSubtype.get() == 'New':
                self.subtypeChoser.grid_forget()
                self.confirm.grid_forget()
                self.newSubtypeEntry = ttk.Entry(self.master)
                self.newSubtypeEntry.grid(row=3, column=self.maxcol+2)
                self.confirm = ttk.Button(self.master, text='Confim.', command=lambda: self.confirmNew('new_subtype', self.newCat))
                self.confirm.grid(row=4, column=self.maxcol+2)
            else:
                self.data[self.newCat] = 0
                self.catagories.append(self.newCat)
                self.subtypes.append(self.newSubtype.get())
                self.subtypeChoser.grid_forget()
                self.confirm.grid_forget()
                self.typeLabel.grid_forget()
                self.catVal[catagory] = ttk.Entry(self.master, validate="key", validatecommand=(self.val_numb, '%P'))
                self.catVal[catagory].grid(row=2, column=self.maxcol+2)
                self.catVal[catagory].insert(tk.END, 0)
                self.entries[self.newCat] = self.catVal[catagory]
                self.gridNew()
        else: # if stage = new_subtype
            self.data[self.newCat] = 0
            self.catagories.append(self.newCat)
            self.subtypes.append(self.newSubtypeEntry.get())
            self.newSubtypeEntry.grid_forget()
            self.confirm.grid_forget()
            self.typeLabel.grid_forget()
            self.catVal[catagory] = ttk.Entry(self.master, validate="key", validatecommand=(self.val_numb, '%P'))
            self.catVal[catagory].grid(row=2, column=self.maxcol+2)
            self.catVal[catagory].insert(tk.END, 0)
            self.entries[self.newCat] = self.catVal[catagory]
            self.subtypeChoices.append(self.newSubtypeEntry.get())
            self.subtypeChoser = ttk.OptionMenu(self.master, self.newSubtype, self.subtypeChoices[0], *self.subtypeChoices)
            self.gridNew()

    def gridNew(self):
            self.add_Data.config(state='normal')
            self.add_Comment.config(state='normal')
            self.write_Data.config(state='normal')
            self.plot_Data.config(state='normal')
            self.newNameLabel.grid_forget()
            self.newTypeLabel.grid_forget()
            self.newSubtypeLabel.grid_forget()
            newcol = (len(self.catagories)+1*round(self.newrow/2))%self.maxcol - 1

            if newcol == 0: # we need a new row
                self.newrow += 2
                newcol = 1
            elif newcol == -1:
                newcol = self.maxcol - 1
            self.catName[self.newCat].grid(row=1+self.newrow, column=newcol, sticky=tk.W+tk.E+tk.S+tk.N)
            self.catVal[self.newCat].grid(row=2+self.newrow, column=newcol, sticky=tk.W+tk.E+tk.S+tk.N)

    def addComment(self):
        self.commentDate.set(self.dateChoices[0])
        self.add_Data.config(state='disabled')
        self.add_Comment.grid_forget()
        self.write_Data.config(state='disabled')
        self.plot_Data.config(state='disabled')
        self.dateChoser.grid(row=64, column=0, sticky=tk.W+tk.E+tk.S+tk.N)
        self.new_Comment.delete(0,tk.END)
        self.new_Comment.grid(row=64, column=1, columnspan=self.maxcol-2, sticky=tk.W+tk.E+tk.S+tk.N)
        self.confirm_Comment.grid(row=64, column=self.maxcol-1, columnspan=1, sticky=tk.W+tk.E+tk.S+tk.N)

    def updateComment(self, value):
        self.ind = self.dates.index(value)
        self.new_Comment.delete(0,tk.END)
        if self.comments[self.ind]:
            self.new_Comment.insert(tk.END, self.comments[self.ind])
        else:
            self.new_Comment.insert(tk.END, '')

    def saveComment(self):
        try: # necessary if no date is selected
            self.comments[self.ind] = self.new_Comment.get()
        except AttributeError:
            pass
        self.dateChoser.grid_forget()
        self.new_Comment.grid_forget()
        self.confirm_Comment.grid_forget()
        self.add_Comment.grid(row=64, column=0, columnspan=self.maxcol, sticky=tk.W+tk.E+tk.S+tk.N)
        self.add_Data.config(state='normal')
        self.write_Data.config(state='normal')
        self.plot_Data.config(state='normal')

    def writeData(self):
        # Reorganize GUI #
        self.titleLabel.grid(columnspan=len(self.catagories))
        self.endLabel.grid(columnspan=len(self.catagories))
        for col,catagory in enumerate(self.catagories):
            self.catName[catagory].grid_forget()
            self.catVal[catagory].grid_forget()
        self.add_Data.grid_forget()
        self.write_Data.grid_forget()
        self.add_Comment.grid_forget()
        self.dateChoser.grid_forget()
        self.new_Comment.grid_forget()
        self.confirm_Comment.grid_forget()
        self.plot_Data.config(state='disabled')
        self.plot_Data.grid(columnspan=len(self.catagories), sticky=tk.W+tk.E+tk.S+tk.N)

        self.catConfirm = {}
        self.typConfirm = {}
        self.subConfirm = {}
        self.dataConfirm = {}

        for col,cat in enumerate(self.catagories):
            if col == 0: # Make data list #
                self.data[cat] = self.entries[cat].get()
            else:
                try:
                    self.data[cat] = str(round(float(self.entries[cat].get()),2))
                except ValueError:
                    self.data[cat] = '0.0'
            self.dataList = list(self.data.values())

            self.catConfirm[cat] = ttk.Label(self.master, text=''.join('  ' + self.catagories[col] + '  '))
            self.catConfirm[cat].grid(row=1, column=col, columnspan=1, sticky=tk.W+tk.E+tk.S+tk.N)
            self.typConfirm[cat] = ttk.Label(self.master, text=''.join(self.types[col]))
            self.typConfirm[cat].grid(row=2, column=col, columnspan=1, sticky=tk.W+tk.E+tk.S+tk.N)
            self.subConfirm[cat] = ttk.Label(self.master, text=''.join(self.subtypes[col]))
            self.subConfirm[cat].grid(row=3, column=col, columnspan=1, sticky=tk.W+tk.E+tk.S+tk.N)
            self.dataConfirm[cat] = ttk.Label(self.master, text=''.join(self.dataList[col]))
            self.dataConfirm[cat].grid(row=4, column=col, columnspan=1, sticky=tk.W+tk.E+tk.S+tk.N)

        # comments
        self.comLabel= ttk.Label(self.master, text='New comments:')
        self.comLabel.grid(row=5, column=0, columnspan=len(self.catagories), sticky=tk.W+tk.E+tk.S+tk.N)

        numnewcom = 0
        self.comConfirm = {}
        self.comConfirmDate = {}
        oldcomment = self.cur_data['comment'] + [None]
        for i,comment in enumerate(self.comments):
            if comment != oldcomment[i]:
                self.comConfirmDate[numnewcom] = ttk.Label(self.master, text=self.dates[i])
                self.comConfirm[numnewcom] = ttk.Label(self.master, text=comment)
                self.comConfirmDate[numnewcom].grid(row=6+numnewcom, column=0, columnspan=1, sticky=tk.W+tk.E+tk.S+tk.N)
                self.comConfirm[numnewcom].grid(row=6+numnewcom, column=1, columnspan=len(self.catagories)-1, sticky=tk.W+tk.E+tk.S+tk.N)
                numnewcom += 1

        self.cancel = ttk.Button(self.master, text='CANCEL', command=lambda: self.cancelWrite())
        self.cancel.grid(row=6+numnewcom,column=0,columnspan=len(self.catagories), sticky=tk.W+tk.E+tk.S+tk.N)

        self.confirm = ttk.Button(self.master, text='Confim Data Entry!', command=lambda: self.confirmWrite())
        self.confirm.grid(row=7+numnewcom,column=0,columnspan=len(self.catagories), sticky=tk.W+tk.E+tk.S+tk.N)

    def confirmWrite(self):
        self.confirm.grid_forget()
        self.cancel.grid_forget()
        self.plot_Data.config(state='normal')

        # write data! #
        wrt.writeDataToFile(filename=self.filename,data=self.dataList,catagories=self.catagories,types=self.types,subtypes=self.subtypes,comments=self.comments,cur_data=self.cur_data)

    def cancelWrite(self):
        self.confirm.grid_forget()
        self.cancel.grid_forget()
        self.comLabel.grid_forget()
        for key in self.comConfirm.keys():
            self.comConfirm[key].grid_forget()
            self.comConfirmDate[key].grid_forget()
        self.newrow = 0 # reset for gridding
        for ind,cat in enumerate(self.catagories):
            self.catConfirm[cat].grid_forget()
            self.typConfirm[cat].grid_forget()
            self.subConfirm[cat].grid_forget()
            self.dataConfirm[cat].grid_forget()
            if ind == 0:
                col = ind
            else:
                if (ind+1*round(self.newrow/2))%self.maxcol == 0:
                    self.newrow += 2
                if self.newrow == 0:
                    col = (ind+1*round(self.newrow/2)) - round(self.maxcol*self.newrow/2)
                else:
                    col = (ind+1*round(self.newrow/2)) - round(self.maxcol*self.newrow/2)
                    if col == -1:
                        col = self.maxcol - 1
            self.catName[cat].grid(row=1+self.newrow, column=col, sticky=tk.W+tk.E+tk.S+tk.N)
            self.catVal[cat].grid(row=2+self.newrow, column=col)
        self.titleLabel.grid(columnspan=self.maxcol)
        self.endLabel.grid(columnspan=self.maxcol)
        self.add_Data.grid(row=63, column=0, columnspan=self.maxcol, sticky=tk.W+tk.E+tk.S+tk.N)
        self.add_Comment.grid(row=64, column=0, columnspan=self.maxcol, sticky=tk.W+tk.E+tk.S+tk.N)
        self.write_Data.grid(row=65, column=0, columnspan=self.maxcol, sticky=tk.W+tk.E+tk.S+tk.N)
        self.plot_Data.config(state='normal')
        self.plot_Data.grid(columnspan=self.maxcol)

    def plotData(self):
        plt.plotThedata(filename=self.filename)

root = tk.Tk()
root.style = ttk.Style()
root.style.theme_use('clam') # 'winnative', 'clam', 'alt', 'default', 'classic', 'vista', 'xpnative'
root.style.configure('TLabel', background = '#7171C6', anchor='center')
root.style.configure('TButton', background = 'gold1')
MainApplication(root)
root.mainloop()
