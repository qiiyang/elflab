"""Defines a series of conceptual classes for the galileo utility"""


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
        
    def log(self, dataLock):  # Write the data to storage; dataLock is a thread-level Lock object
        raise Exception("!!Galileo ERROR!! Data logging method not implemented!!!")
        
    def finish(self):   # To be executed when measurements are terminated, for closing files etc
        raise Exception("!!Galileo ERROR!! Experiment finishing not implemented!!!")

        
class ML_Experiment(ExperimentBase):
    """An experiment defined by a Measurer object and a Logger object"""
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
        
    def log(self, dataLock):
        with dataLock:
            dataToLog = self.currentValues.copy()
        self.logger.log(dataToLog)
        
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
