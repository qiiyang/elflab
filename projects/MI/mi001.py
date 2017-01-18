""" Common definitions / whatever shared for all Janis He-3 related scripts
"""
import time
import csv
import numpy as np

from elflab import uis, datasets

from elflab.devices.lockins import stanford
from elflab.devices.thermometers.rtd import RTD
from elflab.devices.magnets import fake_magnets

import elflab.abstracts as abstracts
import elflab.dataloggers.csvlogger as csvlogger


GPIB_SR830 = 10
GPIB_SR830_2 = 12


# Conversion between data names and indices and labels etc.

VAR_ORDER = ["n", "t", "T", "H", "X", "Y", "t_therm", "t_magnet", "t_lockin", "I_therm", "V_therm", "I_mag", "f", "V_in", "R", "theta"]

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
                 

#SENS_RANGE = (0.1, 0.8)
    
class MI_GUI(uis.GenericGUI):
    DEFAULT_FOLDER = r"D:\MI_Data\test"
    DEFAULT_FN = r"test"

    
# Generic MI experiment with unspecified thermometer and magnet
class MI_SR830_Abstract(abstracts.ExperimentBase):
    # "Public" Variables
    title = "MI"
    
    default_params = {
        "sampling interval / s": "0.1",
        
        "MI SR830 GPIB": "{:d}".format(GPIB_SR830),
        "MI R_series / Ohm": "no entry"
    }
    
    var_order = VAR_ORDER.copy()    # order of variables
    var_titles = VAR_TITLES.copy()    # matching short names with full titles  = {e.g "H": "$H$ (T / $\mu_0$)"}
    format_strings = VAR_FORMATS.copy()   # Format strings for the variables
    
    plotXYs = [
            [("T", "X"), ("T", "Y")],
            [("t", "T"), ("t", "f")]
            ]
    
    default_comments = ""
    
    def __init__(self, params, filename, thermometer, magnet):
        # Save parameters
        self.thermometer = thermometer
        self.magnet = magnet
         
        gpib = int(params["MI SR830 GPIB"])
        self.mi_lockin = stanford.SR830(gpib)
    
        self.measurement_interval = float(params["sampling interval / s"])
        
        self.Rs_mi = float(params["MI R_series / Ohm"])
        
        # Initialise variables
        self.current_values = VAR_INIT.copy()
        self.var_titles = VAR_TITLES.copy()
        
        # create a csv logger
        self.logger = csvlogger.Logger(filename, self.var_order, self.var_titles, self.format_strings)
        
    
    def start(self):
        # Connect to instruments
        self.thermometer.connect()
        self.mi_lockin.connect()
        
        # Reset counter and timer
        self.n = 0
        self.t0 = time.time() - time.perf_counter()
        # Start the csv logger
        self.logger.start()
        
    def measure(self):
        self.current_values["n"] += 1
        self.current_values["t"] = self.t0 + time.perf_counter()
        (self.current_values["t_therm"], self.current_values["T"], self.current_values["I_therm"], self.current_values["V_therm"]) = self.thermometer.read()
        (self.current_values["t_mag"], self.current_values["H"], self.current_values["I_mag"]) = self.magnet.read()
        (self.current_values["t_lockin"], self.current_values["X"], self.current_values["Y"], self.current_values["R"], self.current_values["theta"], self.current_values["f"], self.current_values["V_in"]) = self.mi_lockin.read()
        
    def log(self, dataToLog):
        self.logger.log(dataToLog)
        
    # A perpetual sequence
    def sequence(self):
        while True:
            yield True
        
    def finish(self):
        self.logger.finish()

    
    
# Using two SR830 lock-in amplifiers, and an RTD as the thermometer
class MI_RTD(MI_SR830_Abstract):
    # "Public" Variables
    title = "MI with RTD"
    
    default_params = {
        "sampling interval / s": "0.1",
        
        "RTD SR830 GPIB": "{:d}".format(GPIB_SR830_2),
        "RTD R_series / Ohm": "no entry",
        
        "MI SR830 GPIB": "{:d}".format(GPIB_SR830),
        "MI R_series / Ohm": "no entry"
    }
       
    default_comments = ""
    
    def __init__(self, params, filename):
        # Save parameters
        gpib = int(params["RTD SR830 GPIB"])
        rtd_lockin = stanford.SR830(gpib)
        rtd_Rs = float(params["RTD R_series / Ohm"])
        thermometer = RTD(rtd_lockin, rtd_Rs)
        
        magnet = fake_magnets.ConstMagnet()
        p = params.copy()
         
        super().__init__(p, filename, thermometer, magnet) 