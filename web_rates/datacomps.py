#!/home/chad/anaconda/bin/python
from pymongo import MongoClient
import pandas as pd
import sys

DATABASE = 'VRBO_scenic_hwy_98'
STAT_COLLECTION = 'Stats'
CAL_COLLECTION = 'Calendars'

def getRatesDataFrame():
    client = MongoClient()
    db = client[DATABASE]
    collection = db[CAL_COLLECTION]

    properties = collection.find()
    rates = pd.DataFrame()
    occupied = pd.DataFrame()
    for prop in properties:
        pid = prop['_id']
        a = prop.keys()[0]
        del prop['_id']
        p = pd.DataFrame.from_dict(prop,orient='index')
        if 'Weekly' in p.columns and 'am' in p.columns:
            rates[pid] = pd.Series(p['Weekly'],p.index)
            occupied[pid] = pd.Series(p['am'],p.index)
            print pid,'*'
        else:
            print pid
#    rates.to_csv('rates_'+DATABASE)
#    occupied.to_csv('occupied_'+DATABASE)
    writer = pd.ExcelWriter('rates.xlsx',engine='xlsxwriter')
    #print rates
    rates.to_excel(writer,sheet_name='rates')
    occupied.to_excel(writer,sheet_name='occupancy')
    writer.save()

def getVitalStats():
    client = MongoClient()
    db = client[DATABASE]
    collection = db[STAT_COLLECTION]
    ratescoll = db[CAL_COLLECTION]

    ids = [p['_id'] for p in collection.find({'Bedrooms':'1'})]
    properties = ratescoll.find({'_id':{'$in':ids}})
    
    rates = pd.DataFrame()
    occupied = pd.DataFrame()
    for prop in properties:
        pid = prop['_id']
        a = prop.keys()[0]
        del prop['_id']
        p = pd.DataFrame.from_dict(prop,orient='index')
        if 'Weekly' in p.columns and 'am' in p.columns:
            rates[pid] = pd.Series(p['Weekly'],p.index)
            occupied[pid] = pd.Series(p['am'],p.index)
            print pid,'*'
        else:
            print pid
    rates.to_csv('rates')
    occupied.to_csv('occupied')

def readInputFile(filename):
        lines = open(filename).readlines()
        args = {}
        for line in lines:
            qline = line.split(':')
            k = qline[0].strip()
            v = qline[1].strip()
            if k == 'vrbonumbers':
                args[k] = v.split()
            else:
                args[k] = v

        return args['DATABASE']

getRatesDataFrame()
