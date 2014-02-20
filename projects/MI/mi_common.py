""" Common definitions / whatever shared for all MI-probe related scripts
"""
import time
import elflab.abstracts as abstracts
import elflab.dataloggers.csvlogger as csvlogger

# Conversion between data names and indices and labels etc.

VAR_LIST = ["n", "t", "T", "H", "X", "Y", "t_therm", "t_magnet", "t_lockin", "I_therm", "V_therm", "I_mag", "f", "V_in", "R", "theta"]

# Everything in SI

VAR_DESC = {
            "n": "no. of data points",
            "t": "timestamp, absolute, in s",
            "T": "temperature / K",
            "H": "magnetic field, in T",
            "X": "lock-in X reading, in V",
            "Y": "lock-in Y reading, in V",
            "t_therm": "thermometer timestamp, relative",
            "t_magnet": "magnet timestamp, relative",
            "t_lockin": "lock-in timestamp, relative",
            "I_therm": "thermometer current",
            "V_therm": "thermometer voltage",
            "I_mag": "magnet current",
            "f": "lock-in frequency",
            "V_in": "input voltage",
            "R": "R on the lock-in",
            "theta": "theta on the lock-in"
            }
            
VAR_TITLES = {
            "n": "n",
            "t": "t / s",
            "T": "T / K",
            "H": "H / T",
            "X": "X / V",
            "Y": "Y / V",
            "t_therm": "t_therm / s",
            "t_magnet": "t_magnet / s",
            "t_lockin": "t_lockin / s",
            "I_therm": "I_therm / A",
            "V_therm": "V_therm / V",
            "I_mag": "I_mag / A",
            "f": "f / Hz",
            "V_in": "V_in / V",
            "R": "R / V",
            "theta": "theta / degree"
            }
            
VAR_FORMATS = {
            "n": "{:n}",
            "t": "{:.8f}",
            "T": "{:.10e}",
            "H": "{:.10e}",
            "X": "{:.10e}",
            "Y": "{:.10e}",
            "t_therm": "{:.8f}",
            "t_magnet": "{:.8f}",
            "t_lockin": "{:.8f}",
            "I_therm": "{:.10e}",
            "V_therm": "{:.10e}",
            "I_mag": "{:.10e}",
            "f": "{:.10e}",
            "V_in": "{:.10e}",
            "R": "{:.10e}",
            "theta": "{:.2f}"
            }
            
VAR_INIT = {
            "n": 0,
            "t": 0.,
            "T": 0.,
            "H": 0.,
            "X": 0.,
            "Y": 0.,
            "t_therm": 0.,
            "t_magnet": 0.,
            "t_lockin": 0.,
            "I_therm": 0.,
            "V_therm": 0.,
            "I_mag": 0.,
            "f": 0.,
            "V_in": 0.,
            "R": 0.,
            "theta": 0.
            }
                 

SENS_RANGE = (0.2, 0.8)
                 
class MI_JustMeasure(abstracts.ExperimentBase):
    title = "Mutual Inductance: keep measuring"
    def __init__(self, thermometer, magnet, lockin, logfilename):
        # Save parameters
        self.thermometer = thermometer
        self.magnet = magnet
        self.lockin = lockin
        
        # Initialise variables
        self.currentValues = VAR_INIT.copy()
        self.varTitles = VAR_TITLES.copy()
        
        # create a csv logger
        self.logger = csvlogger.Logger(logfilename, VAR_LIST, VAR_TITLES, VAR_FORMATS)
        
    
    def start(self):
        # Connect to instruments
        self.thermometer.connect()
        self.lockin.connect()
        self.lockin.setAutoSens(*SENS_RANGE)
        # Reset counter and timer
        self.n = 0
        self.t0 = time.time()
        time.perf_counter()
        # Start the csv logger
        self.logger.start()
        
    def measure(self):
        self.currentValues["n"] += 1
        self.currentValues["t"] = self.t0 + time.perf_counter()
        (self.currentValues["t_therm"], self.currentValues["T"], self.currentValues["I_therm"], self.currentValues["V_therm"]) = self.thermometer.read()
        (self.currentValues["t_mag"], self.currentValues["H"], self.currentValues["I_mag"]) = self.magnet.read()
        (self.currentValues["t_lockin"], self.currentValues["X"], self.currentValues["Y"], self.currentValues["R"], self.currentValues["theta"], self.currentValues["f"], self.currentValues["V_in"]) = self.lockin.read()
        
    def log(self, dataToLog):
        self.logger.log(dataToLog)
        
    # A perpetual sequence
    def sequence(self):
        while True:
            yield True
        
    def finish(self):
        self.logger.finish()
        del self.thermometer
        del self.magnet
        del self.lockin
