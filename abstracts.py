######################################################################################################
# Define the base classes
######################################################################################################

class KernelBase:
    """Base class for kernels"""
    title = None
    def __init__(self):
        self.flag_stop = None
        self.flag_quit = None
        self.flag_pause = None
        raise Exception("!!ERROR!! kernel class not implemented!!!")
    def start(self):
        raise Exception("!!ERROR!! kernel class not implemented!!!")
    def stop(self):
        raise Exception("!!ERROR!! kernel class not implemented!!!")
    def quit(self):
        raise Exception("!!ERROR!! kernel class not implemented!!!")
    def pause(self):
        raise Exception("!!ERROR!! kernel class not implemented!!!")
    def resume(self):
        raise Exception("!!ERROR!! kernel class not implemented!!!")
    def plot(self):
        raise Exception("!!ERROR!! kernel class not implemented!!!")
    def autoScaleOn(self):
        raise Exception("!!ERROR!! kernel class not implemented!!!")
    def autoScaleOff(self):
        raise Exception("!!ERROR!! kernel class not implemented!!!")
    def clearPlot(self):
        raise Exception("!!ERROR!! kernel class not implemented!!!")

# Base classes for UI

class UIBase:
    """Base class for user interface"""
    def __init__(self):
        raise Exception("!!ERROR!! UI class not implemented!!!")
        
    def start(self):    # starting the UI
        raise Exception("!!ERROR!! UI start() not implemented!!!")
        
        
# classes to define experiments taken with Galileo Utility
class ExperimentBase:
    """A minimal abstraction of an experiment"""
    
    # "Public" Variables
    currentValues = None   # = {"name": "value"}
    varTitles = None    # matching short names with full titles  = {e.g "H": "$H$ (T / $\mu_0$)"}
    
    title = None    # Title of the Experiment
    plotXYs = None
    parameters = None
    
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
        
    def sequence(self):   # a python generator serves as a control sequence, called before each measurements
        raise Exception("!!Galileo ERROR!! Experiment finishing not implemented!!!")
        
    def finish(self):   # To be executed when measurements are terminated, for closing files etc
        raise Exception("!!Galileo ERROR!! Experiment finishing not implemented!!!")        
        
class LoggerBase:
    """A minimal abstraction of data-logging"""
    def __init__(self, filename=None, comments=None):
        raise Exception("!!Galileo ERROR!! Data-Logger initialisation not implemented!!!")
        
    def start(self):
        raise Exception("!!Galileo ERROR!! Logger start() not implemented!!!")
    
    def log(self, dataToLog):  # To write down a data point
        raise Exception("!!Galileo ERROR!! Data-Logging method not implemented!!!")
        
    def finish(self):
        raise Exception("!!Galileo ERROR!! Data-Logging finishing not implemented!!!")

class ControllerBase:
    """Controller Base Class"""
    def __init__(self, experiment, instrument_lock, data_lock):
        raise Exception("controller class not implimented")
        
# classes for data sets
class DataSetBase(dict):
    """base class for a dataset, defined as {"key": 1D numpy_array} """
    length = None
    sorted_views = None
    errors = None   # errors stored as a dict of numpy arrays
    titles = None   # full titles of the variables
    def empty(self):
        raise Exception("!!Elflab ERROR!! DataSet class not implemented!!!")
    def duplicate(self):
        raise Exception("!!Elflab ERROR!! DataSet class not implemented!!!")
    def sort(self, key):
        raise Exception("!!Elflab ERROR!! DataSet class not implemented!!!")
    def interpolator(self, x, y):
        raise Exception("!!Elflab ERROR!! DataSet class not implemented!!!")