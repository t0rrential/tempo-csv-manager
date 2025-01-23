from csv import DictReader
from math import ceil
from os.path import getmtime
import datetime
from json import dumps

def dictToJson(inputDict: dict):
    dataDict = {}
    totalprofits = 0

    for key in inputDict.keys():
        
        with open("csv\\" + inputDict[key]['path'], 'r') as file:
            reader = DictReader(file)
            
            for row in reader:
                if (row[' Price'] != ' N/A'):
                    price, cents = [int(x) for x in row[' Price'].replace(' ', '').split('.')]
                    profits = inputDict[key]['profit'] - price
                    back = int(row[' Backroom Stock'].replace(' ', ''))
                    floor = int(row[' Floor Stock'].replace(' ', ''))
                    
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
    
    with open("csv\\" + csvName, "r") as file:
        reader = DictReader(file)
        
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

def getLastModifiedTime(csvPath):
    csvPath = "csv\\" + csvPath
    
    timestamp = getmtime(csvPath)
    date = datetime.date.fromtimestamp(timestamp)
    formatted = date.strftime("%m/%d/%Y")
    
    return formatted