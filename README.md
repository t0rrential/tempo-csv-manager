<p align="center">
  <img src="https://raw.githubusercontent.com/t0rrential/tempo-csv-manager/refs/heads/main/resource/logo.png" alt="tcm logo"/>
</p>

# tempo-csv-manager

python project designed to work with tempo monitor csvs, for windows 10/11.

<p align="center">
  <img src="https://raw.githubusercontent.com/t0rrential/tempo-csv-manager/refs/heads/main/resource/KMmbZZVUeV.png" alt="feature 1"/>
  <img src="https://raw.githubusercontent.com/t0rrential/tempo-csv-manager/refs/heads/main/resource/PaoyuMzNTo.png" alt="feature 2"/>
</p>

features:  
• shortest path between all stores using travelling-salesman problem solver  
• stores sortable by distance, profitability, and cost/profit ratio  
• google maps api integration for distance and map photos  
• dark theme / light theme  

## setup

this project is still under development. if you would like to try it out for yourself, go over to the [build branch](https://github.com/t0rrential/tempo-csv-manager/tree/build) of this project and clone it to your local workspace.

```bash
pip install -r requirements.txt
```

from there, make a .env file with the following format:

```python
GOOGLE_MAPS_APIKEY= # valid google maps apikey here
HOME_ADDRESS= # valid home address here
```

you can then run ```main.py```.

## to-do
• discord integration  
• qthread so that nothing gets stuck on the main thread / ui does not hang  
• rework handling of google maps api  
• debloat and fragment large classes into managable subclasses  
• switch from json data handling to sqlite db  
• ui redesign  
