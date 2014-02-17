class ExperimentBase:
    """A minimal abstraction of an experiment"""
    
    # "Public" Variables
    dataPoint = None   # = {"name": "value"}
    namesAndUnits = None    # = {e.g "H": "$H$ (T / $\mu_0$)"}
    
    title = None    # Title of the Experiment
    
    def __init__(self):
        raise Exception("!!Galileo ERROR!! Experiment initialisation not implemented!!!")
    
    def measure(self):  # Trigger a measurement
        raise Exception("!!Galileo ERROR!! Measurement triggering method not implemented!!!")
        
    def log(self, dataLock):  # Write the data to storage; dataLock is a thread-level Lock object
        raise Exception("!!Galileo ERROR!! Data logging method not implemented!!!")
        
    def finish(self):   # To be executed when measurements are terminated, for closing files etc
        raise Exception("!!Galileo ERROR!! Experiment finishing not implemented!!!")

class MeasurerBase:
    """A minimal abstraction of a measurement"""
    dataPoint = None # = {"name": "value"}
    namesAndUnits = None # = {e.g "H": "$H$ (T / $\mu_0$)"}
    
    def __init__(self):
        raise Exception("!!Galileo ERROR!! Measurer initialisation not implemented!!!")
    
    def measure(self):  # Trigger a measurement
        raise Exception("!!Galileo ERROR!! Measurement triggering method not implemented!!!")
        
    def finish(self):
        raise Exception("!!Galileo ERROR!! Measurer finishing not implemented!!!")

        

class LoggerBase:
    """A minimal abstraction of data-logging"""
    def __init__(self):
        raise Exception("!!Galileo ERROR!! Data-Logger initialisation not implemented!!!")
    
    def log(self, dataPoint):  # To write down a data point
        raise Exception("!!Galileo ERROR!! Data-Logging method not implemented!!!")
        
    def finish(self):
        raise Exception("!!Galileo ERROR!! Data-Logging finishing not implemented!!!")


        
class MeasurerAndLogger(ExperimentBase):
    """An experiment defined by a Measurer object and a Logger object"""
    def __init__(self, title, measurer, logger):
        self.title = title
        self.measurer = measurer
        self.logger = logger
        self.dataPoint = measurer.dataPoint
        self.namesAndUnits = measurer.namesAndUnits
        
    def measure(self):
        self.measurer.measure()
        
    def log(self, dataLock):
        with dataLock:
            dataToLog = self.dataPoint.copy()
        self.logger.log(dataToLog)
        
    def finish(self):
        self.measurer.finish()
        self.logger.finish()
        