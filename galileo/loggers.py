import elflab.galileo.model_experiments as models
import time

class CSVLogger(models.LoggerBase):
    """Implementing a Logger writing a CSV file"""
    
    def __init__(self, filename, varlist, save_every=10., buffering=-1, dialect='excel', **fmtparams):
                #(self, file path/name, ["var names"], saving interval, [parameters for python buffering and csv writers])
        print("        [CSV Logger:] Data will be logged in the file:\n{}\n".format(filename))
        # Save parameters
        self.filename = filename
        self.varlist = varlist
        self.save_every = save_every
        self.buffering = buffering
        
        # Initialise the file and writing the header row