# TO-DO:
# make this genuinely freaking modular

# currently only the json part is modular, this entire script
# still holds all the stores in a single variable. nothing has
# changed from the original processing.py

from json import dumps, load
from os import getenv, path, makedirs
from dotenv import load_dotenv
import googlemaps.addressvalidation
import googlemaps.client
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

    def load_store_data(self, address : str):
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
        # print(len(self.store_files.keys()))
    
    def findCoordinates(self):
        for address in self.addresses:
            if "coordinates" not in self.store_files[address].keys():
                response = self.gclient.geocode(urllib.parse.quote_plus(address))
                
                self.store_files["coordinates"] = response[0]["geometry"]["location"]
                self.store_files["coordinate_response"] = response
                
                self.save_store_data(address)
                
    def addressPermutations(self):
        for address in self.addresses:
            # finding unique addresses that have not been added to the added_permutations list
            uniques = list(set(self.addresses) - set(self.store_files[address]['added_permutations']))
            
            if len(uniques) > 0:
                for unique_address in uniques:
                    self.store_files[address]['permutations'].append([unique_address, address])
                    self.store_files[address]['added_permutations'].append(unique_address)
                    
            self.save_store_data(address)
            
    def addressMatrix(self):
        for address in self.addresses:
            for pair in self.store_files[address]['permutations']:
                addr1, addr2 = pair
                if (addr1 in self.addresses) and (addr2 in self.addresses):
                    if addr1 not in self.store_files[addr2]['distances'].keys() or addr2 not in self.store_files[addr1]['distances'].keys():
                        try:
                            # print(f"working on {pair}")
                            
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
        """Finds the time between two addresses that have been stored in self.store_files."""
        address = self.addresses[address]
        target = self.addresses[target]
        
        return self.store_files[address]['distances'][target]['response']['rows'][0]['elements'][0]['duration']['value']
    
    def travellingSalesman(self, numStores : int, numMins: int):
        """Applies a travelling salesman solver to the info stored in self.store_files."""
        totaltime = 0
        formatted_tsp = []
        # formatted_tsp[n] = [addr1, addr2, dist]

        # loop logic goes as follows:
        # for address in self.addresses, make another loop going through distance responses
        # check the targetted address is within numStores. if so, append to formatted_tsp
        for address in self.addresses[:numStores]:
            for target in self.store_files[address]['distances'].keys():
                if target in self.addresses[:numStores]:
                    formatted_tsp.append((self.addresses.index(address), self.addresses.index(target), self.store_files[address]["distances"][target]['distance']))

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
    
    def run(self, numStores, numMins):
        """Runs prefill(), findCoordinates(), addressPermutations(), addressMatrix(), and returns travellingSalesman()."""
        self.prefill()
        self.findCoordinates()
        self.addressPermutations()
        self.addressMatrix()
        final = self.travellingSalesman(numStores, numMins)
        
        return final
    
    def storeCount(self):
        """Returns number of store addresses."""
        return len(self.addresses)
    
    def extractData():
        """Returns a dict with data.txt loaded."""
        if path.exists("data.txt"):
            with open("data.txt", "r") as f:
                return load(f)
            
    def checkKey(testKey):
        """Check if a given Google Maps API key is valid."""
        try:
            testClient = googlemaps.Client(key=testKey)
        except:
            return False
        try:
            # Make a simple geocoding request
            geocode_result = testClient.geocode("1600 Amphitheatre Parkway, Mountain View, CA")

            # Check if the request was successful
            if geocode_result:
                return True
            else:
                return False
        except googlemaps.exceptions.ApiError as e:
            return False
        
    def checkAddress(testKey, testAddress):
        """Check if a given address is valid using the Google Maps API."""
        testClient = googlemaps.Client(key=testKey)
        address_result = {}
        
        try:
            address_result = googlemaps.addressvalidation.addressvalidation(client=testClient, addressLines=[testAddress])
        except:
            return False
        
        if 'error' not in address_result.keys():
            if address_result['result']['address']['addressComponents'][0]['confirmationLevel'] == "CONFIRMED":
                return True
        return False
    
    def getHomeAddress():
        return HOME_ADDRESS