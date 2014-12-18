"""Defines a series of conceptual classes"""

# classes to define experiments taken with Galileo Utility
class ExperimentBase:
    """A minimal abstraction of an experiment"""
    
    # "Public" Variables
    currentValues = None   # = {"name": "value"}
    varTitles = None    # matching short names with full titles  = {e.g "H": "$H$ (T / $\mu_0$)"}
    
    title = None    # Title of the Experiment
    
    def __init__(self):
        raise Exception("!!Galileo ERROR!! Experiment initialisation not implemented!!!")
        
    def start(self):    # Start the experiment
        raise Exception("!!Galileo ERROR!! Experiment start() not implemented!!!")
    
    def measure(self):  # Trigger a measurement
        raise Exception("!!Galileo ERROR!! Measurement triggering method not implemented!!!")
        
    def log(self, dataToLog):  # Write the data to storage; dataToLog is the data to log
        raise Exception("!!Galileo ERROR!! Data logging method not implemented!!!")
        
    def sequence(self):   # a python generator serves as a control sequence, called before each measurements
        raise Exception("!!Galileo ERROR!! Experiment control sequence not implemented!!!")
        
    def finish(self):   # To be executed when measurements are terminated, for closing files etc
        raise Exception("!!Galileo ERROR!! Experiment finishing not implemented!!!")

class ExperimentWithLogger(ExperimentBase):
    """An experiment with a pre-defined Logger object"""
    def __init__(self, logger):
        self.logger = logger
        
    def start(self):
        self.logger.start()
        
    def measure(self):  # Trigger a measurement
        raise Exception("!!Galileo ERROR!! Measurement triggering method not implemented!!!")
        
    def log(self, dataToLog):
        self.logger.log(dataToLog)
        
    def sequence(self):   # a python generator serves as a control sequence, called before each measurements
        raise Exception("!!Galileo ERROR!! Experiment control sequence not implemented!!!")
        
    def finish(self):
        self.logger.finish()

    

        
    def log(self, dataToLog):  # Write the data to storage; dataToLog is the data to log
        raise Exception("!!Galileo ERROR!! Data logging method not implemented!!!")
        
    def sequence(self):   # a python generator serves as a control sequence, called before each measurements
        raise Exception("!!Galileo ERROR!! Experiment finishing not implemented!!!")
        
    def finish(self):   # To be executed when measurements are terminated, for closing files etc
        raise Exception("!!Galileo ERROR!! Experiment finishing not implemented!!!")        
        
class ML_Experiment(ExperimentBase):
    """An experiment defined by a Measurer object and a Logger object, without a control sequence"""
    def __init__(self, title, measurer, logger):
        self.title = title
        self.measurer = measurer
        self.logger = logger
        self.currentValues = measurer.currentValues
        self.varTitles = measurer.varTitles
        
    def start(self):
        self.measurer.start()
        self.logger.start()
        
    def measure(self):
        self.measurer.measure()
        
    def log(self, dataToLog):
        self.logger.log(dataToLog)
        
    # No control
    def sequence(self):
        while True:
            yield True
        
    def finish(self):
        self.logger.finish()  
        self.measurer.finish()      
        
        
class Measurer:
    """A minimal abstraction of a measurement"""
    currentValues = None   # = {"name": "value"}
    varTitles = None    # matching short names with full titles  = {e.g "H": "$H$ (T / $\mu_0$)"}
    
    def __init__(self):
        raise Exception("!!Galileo ERROR!! Measurer initialisation not implemented!!!")
        
    def start(self):
        raise Exception("!!Galileo ERROR!! Measurer start() not implemented!!!")
    
    def measure(self):  # Trigger a measurement
        raise Exception("!!Galileo ERROR!! Measurement triggering method not implemented!!!")
        
    def finish(self):
        raise Exception("!!Galileo ERROR!! Measurer finishing not implemented!!!")

        
class Logger:
    """A minimal abstraction of data-logging"""
    def __init__(self):
        raise Exception("!!Galileo ERROR!! Data-Logger initialisation not implemented!!!")
        
    def start(self):
        raise Exception("!!Galileo ERROR!! Logger start() not implemented!!!")
    
    def log(self, dataToLog):  # To write down a data point
        raise Exception("!!Galileo ERROR!! Data-Logging method not implemented!!!")
        
    def finish(self):
        raise Exception("!!Galileo ERROR!! Data-Logging finishing not implemented!!!")

# classes for data sets
class DataSetBase(dict):
    """base class for a dataset, defined as {"key": 1D numpy_array} """
    sorted_views = None
    errors = None
    def empty(self):
        raise Exception("DataSet class not implemented!!!")
    def duplicate(self):
        raise Exception("DataSet class not implemented!!!")
    def sort(self, key):
        raise Exception("DataSet class not implemented!!!")
    def interpolator(self, x, y):
        raise Exception("DataSet class not implemented!!!")    