from csv import DictReader
from math import ceil
from os.path import getmtime
from json import dumps

from src.local.ValidateCsv import csvConverter

import datetime

def dictToJson(inputDict: dict):
    dataDict = {}
    totalprofits = 0

    for key in inputDict.keys():
        reader = DictReader(csvConverter(inputDict[key]['path']))
        
        for row in reader:
            if (row[' Price'] != ' N/A'):
                price, cents = [int(x) for x in row[' Price'].replace(' ', '').split('.')]
                profits = inputDict[key]['profit'] - price
                back = int(row[' Backroom Stock'].replace(' ', ''))
                floor = int(row[' Floor Stock'].replace(' ', ''))
                msrp = float(inputDict[key]["msrp"].replace('$', ''))
                
                if(profits > 0 and (back > 0 or floor > 0)): 
                    address = row['Address'] + ", " + row[' City'] + ", " + row[' State'] + ", " + row[' ZIP']
                    
                    if(address not in dataDict):
                        dataDict[address] = {}
                        dataDict[address]['store_profit'] = 0
                    
                    if('itemList' not in dataDict[address]):
                        dataDict[address]['itemList'] = []
                    
                    fprofits = profits * floor
                    bprofits = profits * back
                    tprofits = fprofits + bprofits
                    
                    dataDict[address][key] =  {
                            'msrp' : msrp,
                            'price' : price, 
                            'profits' : profits, 
                            'fprofits' : fprofits,
                            'bprofits' : bprofits,
                            'tprofits' : tprofits,
                            'floor' : floor, 
                            'back' : back, 
                            'aisle' : row[' Aisles']
                        }
                    
                    dataDict[address]['itemList'].append(key)
                    dataDict[address]['store_profit'] += ceil(tprofits)
                    dataDict[address]['store_profit'] = int(dataDict[address]['store_profit'])
                    totalprofits +=  tprofits

    real = dumps(dataDict, sort_keys=True, indent=4)

    # sortedKeys = sorted(dataDict.keys(), key = lambda k : dataDict[k]['store_profit'], reverse=True)

    with open("data.txt", "w") as fp:
        fp.write(real)
    return

def numProfitableItems(csvName, profit):
    npi = 0
    total = 0
    
    reader = DictReader(csvConverter(csvName))
    
    for row in reader:
            if (row[' Price'] != ' N/A'):
                price, cents = [int(x) for x in row[' Price'].replace(' ', '').split('.')]
                profits = profit - price
                back = int(row[' Backroom Stock'].replace(' ', ''))
                floor = int(row[' Floor Stock'].replace(' ', ''))
                
                if(profits > 0 and (back > 0 or floor > 0)): 
                    npi += back + floor
                
                total += back + floor
    
    return [npi, total]

def itemInfo(csvName):
    last_line = ""
    
    with open("csv\\" + csvName) as f:
        for line in f:
            pass
        last_line = line

    # print(last_line)
    name, msrp = last_line.split(", MSRP: ")
    
    return [name, msrp]

def itemStats(csvName):
    priceList = []
    avg = 0
    low = 0
    
    reader = DictReader(csvConverter(csvName))
    
    for row in reader:
        if (row[' Price'] != ' N/A' and row[' Price'] != None):
            price, cents = [int(x) for x in row[' Price'].replace(' ', '').split('.')]                   
            priceList.append(price)
    
    avg = sum(priceList) / len(priceList)
    low = min(priceList)
    return [avg, low]

def getLastModifiedTime(csvPath):
    csvPath = "csv\\" + csvPath
    
    timestamp = getmtime(csvPath)
    date = datetime.date.fromtimestamp(timestamp)
    formatted = date.strftime("%m/%d/%Y")
    
    return formatted