

import time
import csv
from elflab import abstracts

# Constants
DEFAULT_SAVE_INTERVAL = 10.    # in s

class Logger(abstracts.LoggerBase):
    """Implementing a Logger writing a CSV file"""
    
    # self.Variables:
    
    # everything from the __init__ parameters
    # file
    # csvwriter: a Python cvs writer that writes to file
    
    def __init__(self, filename, var_order, var_titles, format_strings, save_interval=DEFAULT_SAVE_INTERVAL, openKwargs={}, csvKwargs={}):
                #(self, file path/name, ["var names"], {"names": "full titles"}, {"names": "format strings"}, saving interval, additional keyword argument dictionary for python open(), additional keyword arguments dictionary for python csv writer)
        print("        [CSV Logger:] Data will be logged in the file:\n>>>>>>>>>>>>\"{}\"<<<<<<<<<<<<\n".format(filename))
        # Save parameters
        self.filename = filename
        self.var_order = var_order
        self.var_titles = var_titles
        self.format_strings = format_strings
        self.save_interval = save_interval
        self.openKwargs = openKwargs
        self.csvKwargs = csvKwargs
        
    def start(self):
        # Initialise the file and writing the header row
        self.file = open(self.filename, mode="at", newline='', **self.openKwargs)
        self.csvwriter = csv.writer(self.file, **self.csvKwargs)
        
        headerrow = [self.var_titles[varName] for varName in self.var_order]
        self.csvwriter.writerow(headerrow)
        
        # Initialise the timer and save
        self.file.flush()
        self.lastSaved = time.perf_counter()
        
        
    def log(self, dataToLog):
        row = [self.format_strings[varName].format(dataToLog[varName]) for varName in self.var_order]
        self.csvwriter.writerow(row)
        t = time.perf_counter()
        if (t - self.lastSaved) > self.save_interval:
            self.lastSaved = t
            self.file.flush()
            
        
    def finish(self):
        self.file.close()
        
