# Constants
DEFAULT_SAVE_EVERY = 10.    # in s

import time
import csv
from elflab import abstracts

class Logger(abstracts.Logger):
    """Implementing a Logger writing a CSV file"""
    
    # self.Variables:
    
    # everything from the __init__ parameters
    # file
    # csvwriter: a Python cvs writer that writes to file
    
    def __init__(self, filename, varList, varTitles, formatStrings, saveEvery=DEFAULT_SAVE_EVERY, openKwargs={}, csvKwargs={}):
                #(self, file path/name, ["var names"], {"names": "full titles"}, {"names": "format strings"}, saving interval, additional keyword argument dictionary for python open(), additional keyword arguments dictionary for python csv writer)
        print("        [CSV Logger:] Data will be logged in the file:\n>>>>>>>>>>>>\"{}\"<<<<<<<<<<<<\n".format(filename))
        # Save parameters
        self.filename = filename
        self.varList = varList
        self.varTitles = varTitles
        self.formatStrings = formatStrings
        self.saveEvery = saveEvery
        self.openKwargs = openKwargs
        self.csvKwargs = csvKwargs
        
    def start(self):
        # Initialise the file and writing the header row
        self.file = open(self.filename, mode="at", newline='', **self.openKwargs)
        self.csvwriter = csv.writer(self.file, **self.csvKwargs)
        
        headerrow = [self.varTitles[varName] for varName in self.varList]
        self.csvwriter.writerow(headerrow)
        
        # Initialise the timer and save
        self.file.flush()
        self.lastSaved = time.perf_counter()
        
        
    def log(self, dataToLog):
        row = [self.formatStrings[varName].format(dataToLog[varName]) for varName in self.varList]
        self.csvwriter.writerow(row)
        t = time.perf_counter()
        if (t - self.lastSaved) > self.saveEvery:
            self.lastSaved = t
            self.file.flush()
            
        
    def finish(self):
        self.file.close()
        
