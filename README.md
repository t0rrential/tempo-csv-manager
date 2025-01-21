# tempo-csv-manager

todo:  
: save itemid to csv and preload  
: discord integration  
: finish datawindow  
: full datawindow integration into mainwindow and good compatibility with loginwindow  
: add recalc button to loginwindow  
: setup gmaps static image api  
: messagebox for user secrets (home address, gmaps api key, dc token)  
  
other stuff importante  
: check for .env file existence  
: in router, check for .env existence and don't create self.gclient unless the apikey is valid
: in dataWindow, make the option to have distance and distance filters togglable based on whether or not apikey is valid
: in main.py, ensure all things have been setup already (csv folder, store_data folder, )

major rewrites:  
: transfer current system to a sqlite platform with a .db file (easier in every single way lol) 