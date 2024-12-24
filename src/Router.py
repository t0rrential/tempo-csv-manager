
# TO-DO:
# make this genuinely fucking modular

# currently only the json part is modular, this entire script
# still holds all the stores in a single variable. nothing has
# changed from the original processing.py

from json import dumps, load
from os import getenv, path, makedirs, listdir
from dotenv import load_dotenv
from mlrose_ky import TravellingSales, TSPOpt, genetic_alg

import simplekml
import googlemaps
import urllib
import numpy

# Load environment variables
load_dotenv()
HOME_ADDRESS = getenv('HOME_ADDRESS')
GOOGLE_MAPS_APIKEY = getenv("GOOGLE_MAPS_APIKEY")

# Ensure directory exists for individual store files
STORE_DATA_DIR = "store_data"
makedirs(STORE_DATA_DIR, exist_ok=True)

class Router():
    def __init__(self):
        self.store_files = {} # {f.split(".")[0]: f for f in listdir(STORE_DATA_DIR) if f.endswith(".json")}
        self.addresses : list[str] = []  # List of addresses
        self.gclient : googlemaps.Client = googlemaps.Client(key=GOOGLE_MAPS_APIKEY)

    def load_store_data(address : str):
        """Load data for a specific store from its JSON file.\n"""
        filepath = path.join(STORE_DATA_DIR, f'{address.replace(" ", "_")}.json')
        if path.exists(filepath):
            with open(filepath, "r") as f:
                return load(f)
        else:
            boilerplate = {
                'coordinates' : {},
                'coordinate_response' : [],
                'permutations' : [],
                'distances' : {},
                'added_permutations' : []
            }
            return boilerplate
            
    def save_store_data(self, address):
        """Save data for a specific store to its JSON file."""
        filepath = path.join(STORE_DATA_DIR, f'{address.replace(" ", "_")}.json')
        with open(filepath, "w") as f:
            f.write(dumps(self.store_files[address], indent=4))

    def prefill(self):
        if path.exists("data.txt"):
            with open("data.txt", "r") as f:
                self.storedata = load(f)
                self.addresses = sorted(
                    self.storedata.keys(),
                    key=lambda k: self.storedata[k]['store_profit'],
                    reverse=True
                )
                
                self.addresses.insert(0, HOME_ADDRESS)
                for address in self.addresses:
                    self.store_files[address] = self.load_store_data(address)
    
    def findCoordinates(self):
        for address in self.addresses:
            if "coordinates" not in self.store_files[address].keys():
                response = self.gclient.geocode(urllib.parse.quote_plus(address))
                
                self.store_files["coordinates"] = response[0]["geometry"]["location"]
                self.store_files["coordinate_response"] = response
                
                self.save_store_data(address)
                
    # def fixAddressPermutations(self):
    #     for address in self.addresses:
    #         self.store_files[address]["added_permutations"] = []
            
    #         for permutation in self.store_files[address]["permutations"]:
    #             item : list = list(set(permutation) - set([address]))[0]
    #             self.store_files[address]["added_permutations"].append(item)
    #         self.save_store_data(address)
                
    def addressPermutations(self):
        for address in self.addresses:
            # finding unique addresses that have not been added to the added_permutations list
            uniques = list(set(self.addresses) - set(self.store_files[address]['added_permutations']))
            
            if len(uniques) > 0:
                for unique_address in uniques:
                    self.store_files[address]['permutations'].append([unique_address, address])
                    
            self.save_store_data(address)
            
    def addressMatrix(self):
        for address in self.addresses:
            for pair in self.store_files[address]['permutations']:
                addr1, addr2 = pair
                try:
                    print(f"working on {pair}")
                    
                    response = self.gclient.distance_matrix([addr1], [addr2], mode="driving", units="imperial")
                    distance = float(response["rows"][0]["elements"][0]["distance"]["text"].split()[0])
                    
                    self.store_files[addr1]['distances'][addr2] = {
                        'distance': distance,
                        'response' : response
                    }
                    
                    self.store_files[addr2]['distances'][addr1] = {
                        'distance': distance,
                        'response' : response
                    }
                    
                    self.save_store_data(addr1)
                    self.save_store_data(addr2)
                except Exception as e:
                    print(f"error on {pair} with exception {e}")
    
    def findTime(self, address, target):
        address = self.addresses[address]
        target = self.addresses[target]
        
        return self.store_files[address]['distances'][target]['response']['rows'][0]['elements'][0]['duration']['value']
    
    def travellingSalesman(self, numStores : int, numMins: int):
        totaltime = 0
        formatted_tsp = []
        # formatted_tsp[n] = [addr1, addr2, dist]

        # loop logic goes as follows:
        # for address in self.addresses, make another loop going through distance responses
        # check the targetted address is within numStores. if so, append to formatted_tsp
        for address in self.addresses[:numStores]:
            for target in self.store_files[address]['distances'].keys():
                if target in self.addresses[:numStores]:
                    formatted_tsp.append((self.addresses.index(address), self.addresses.index(target), info["distance"]))

        fitness_distances = TravellingSales(distances=formatted_tsp)
        problem_fit = TSPOpt(length=numStores, fitness_fn=fitness_distances, maximize=False)

        best_state, bf, fc = genetic_alg(problem_fit, random_state=2)
        best_state = best_state.tolist()
        best_state = numpy.roll(best_state, best_state.index(0))

        routing = []
        
        for index in best_state:
            routing.append(self.addresses[index])
        # print("In order, best state goes:")
        # for index in best_state:
        #     print(self.addresses[index], end=", ")
        # print()

        for i in range(len(best_state) - 1):
            totaltime += (numMins * 60) + self.findTime(best_state[i], best_state[i + 1])

        totaltime += self.findTime(best_state[0], best_state[-1])
        
        totaltime /= 3600

        #print(f"Total hours will be {totaltime / 3600}")
        
        return {
            'routing': routing,
            'time' : totaltime
        }
    
    def run(self):
        self.prefill()
        self.findCoordinates()
        self.addressPermutations()
        self.addressMatrix()
        final = self.travellingSalesman()
        
        return final