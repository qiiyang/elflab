import time
from elflab import abstracts
  
class Logger(abstracts.Logger):
    """Implementing a Logger writing a CSV file"""
    
    def __init__(self, filename, varlist, save_every=10., openKwargs={}, csvKwargs={}):
                #(self, file path/name, ["var names"], saving interval, additional keyword argument dictionary for python open(), additional keyword arguments dictionary for python csv writer)
        print("        [CSV Logger:] Data will be logged in the file:\n{}\n".format(filename))
        # Save parameters
        self.filename = filename
        self.varlist = varlist
        self.save_every = save_every
        
        # Initialise the file and writing the header row
        self.file = open(filename, mode="at", **openKwargs)
        
        
    def finish(self):
        self.file.close()
        
        