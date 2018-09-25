'''
convert .txt to .json (possible one time use)
change the file names in the last line of the file to contorl operation..
'''

import os
import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

path = os.path.dirname(os.path.dirname(__file__))
os.chdir(path)

def convertThedata(readname, writename):
    # get the stuff
    # adapted from plotting script

    path = os.path.dirname(os.path.dirname(__file__))
    file = open(path + '\\' + readname, 'r')
    catagories = file.readline().strip().split("\t")
    types = file.readline().strip().split("\t")
    subtypes = file.readline().strip().split("\t")

    allData = {}
    lists = {}
    sublists = {}
    for i,catagory in enumerate(catagories):
        if i == 0:
            allData['Date'] = []
        else:
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
                allData['Date'].append(data[i])
            else:
                allData[catagory].append(float(data[i].replace(',', '')))
    file.close()

    # reformat to write_data
    write_data = {}
    write_data['data'] = allData
    write_data['type'] = {}
    write_data['subtype'] = {}
    for i,cat in enumerate(catagories):
        if i == 0:
            write_data['type']['Date'] = 'Date'
            write_data['subtype']['Date'] = 'Date'
        else:
            write_data['type'][cat] = types[i]
            write_data['subtype'][cat] = subtypes[i]
    write_data['comment'] = [None] * len(write_data['data']['Date'])

    with open(writename, 'w') as write_file: #### THIS IS HOW YOU WRITE
        json.dump(write_data, write_file)

convertThedata('data\personalFinancesData.txt', 'data\personalFinancesData_test.json')
