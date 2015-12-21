""" Common definitions / whatever shared for all Janis He-3 related scripts
"""
import time
import csv
import numpy as np

from elflab.devices.T_controllers.lakeshore import Lakeshore340

import elflab.abstracts as abstracts
import elflab.dataloggers.csvlogger as csvlogger


GPIB_LAKESHORE340 = 11
GPIB_DMM = 19

# Conversion between data names and indices and labels etc.

VAR_ORDER = ["n", "t", "T_sample", "H", "T_A", "T_B", "T_sorb", "T_1K", "R1", "R2", "X1", "Y1", "f1", "Vex1", "X2", "Y2", "f2", "Vex2"]

# Everything in SI

VAR_DESC = {
            "n": "no. of data points",
            "t": "timestamp, absolute, in s",
            "T_sample": "sample temperature / K",
            "H": "magnetic field, in T", 
            "T_A": "sample temperature: RuO",
            "T_B": "sample temperature: Si diode",
            "T_sorb": "sorb temperature / K", 
            "T_1K": "1K Pot temperature / K",
            "R1": "Resistance of channel 1 / Ohm",
            "R2": "Resistance of channel 2 / Ohm",
            "X1": "Lockin X on ch 1 / V", 
            "Y1": "Lockin Y on ch 1 / V",
            "f1": "Lockin frequency on ch 1 / Hz",
            "Vex1": "Lockin sine output on ch 1 / V",
            "X2": "Lockin X on ch 2 / V", 
            "Y2": "Lockin Y on ch 2 / V",
            "f2": "Lockin frequency on ch 2 / Hz",
            "Vex2": "Lockin sine output on ch 2 / V"
            }
            
VAR_TITLES = {
            "n": "n",
            "t": "t / s",
            "T_sample": "T_sample / K",
            "T_A": "T_A / K",
            "T_B": "T_B / K",
            "T_sorb": "T_sorb / K", 
            "T_1K": "T_1K / K",
            "H": "H / T",
            "R1": "R1 / Ohm",
            "R2": "R2 / Ohm",
            "X1": "X1 / V", 
            "Y1": "Y1 / V",
            "f1": "f1 / Hz",
            "Vex1": "Vex1 / V",
            "X2": "X2 / V", 
            "Y2": "Y2 / V",
            "f2": "f2 / Hz",
            "Vex2": "Vex2 / V"
            }
            
VAR_FORMATS = {
            "n": "{:n}",
            "t": "{:.8f}",
            "T_sample": "{:.10e}",
            "T_A": "{:.10e}",
            "T_B": "{:.10e}",
            "T_sorb": "{:.10e}", 
            "T_1K": "{:.10e}",
            "H": "{:.10e}",
            "R1": "{:.10e}",
            "R2": "{:.10e}",
            "X1": "{:.10e}",
            "Y1": "{:.10e}",
            "f1": "{:.10e}",
            "Vex1": "{:.10e}",
            "X2": "{:.10e}", 
            "Y2": "{:.10e}",
            "f2": "{:.10e}",
            "Vex2": "{:.10e}"
            }
            
VAR_INIT = {
            "n": 0,
            "t": 0.,
            "T_sample": 0.,
            "T_A": 0.,
            "T_B": 0.,
            "T_sorb": 0., 
            "T_1K": 0.,
            "H": 0.,
            "R1": 0.,
            "R2": 0.,
            "X1": 0.,
            "Y1": 0.,
            "f1": 0.,
            "Vex1": 0.,
            "X2": 0., 
            "Y2": 0.,
            "f2": 0.,
            "Vex2": 0.
            }
                 

SENS_RANGE = (0.1, 0.8)
                 
class JanisS07TwoLockin(abstracts.ExperimentBase):
    # "Public" Variables
    title = "Janis S07 He-3: with Two Lock In Amplifiers"
    current_values = VAR_INIT.copy()   # = {"name": "value"}
    var_titles = VAR_TITLES.copy()    # matching short names with full titles  = {e.g "H": "$H$ (T / $\mu_0$)"}
    
    plotXYs = [[""]
    ]
    default_params = None
    default_comments = ""
    def __init__(self, lockin1, R_series1, lockin2, R_series2, magnet, logfilename):
        # Define the temperature controllers
        self.lakeshore = Lakeshore340(GPIB_LAKESHORE340)
    
        # Save parameters
        self.lockin1 = lockin1
        self.R_series1 = R_series1
        self.lockin2 = lockin2
        self.R_series2 = R_series2
        self.magnet = magnet
        
        # Initialise variables
        self.currentValues = VAR_INIT.copy()
        self.varTitles = VAR_TITLES.copy()
        
        # create a csv logger
        self.logger = csvlogger.Logger(logfilename, VAR_LIST, VAR_TITLES, VAR_FORMATS)
        
    
    def start(self):
        # Connect to instruments
        self.cryocon.connect()
        self.lakeshore.connect()
        self.lockin1.connect()
        self.lockin2.connect()
        self.magnet.connect()
        
        if self.lockin1.is_digital:
            self.lockin1.setAutoSens(*SENS_RANGE)
        if self.lockin2.is_digital:
            self.lockin2.setAutoSens(*SENS_RANGE)
        
        # Reset counter and timer
        self.n = 0
        self.t0 = time.time()
        time.perf_counter()
        # Start the csv logger
        self.logger.start()
        
    def measure(self):
        self.currentValues["n"] += 1
        self.currentValues["t"] = self.t0 + time.perf_counter()
        t,self.currentValues["T_flow"] = self.cryocon.read("A")
        t,self.currentValues["T_sample"] = self.cryocon.read("B")
        t,self.currentValues["T_sorb"] = self.lakeshore.read("A")
        t,self.currentValues["H"],t = self.magnet.read()
        t,self.currentValues["X1"],self.currentValues["Y1"],t,t,self.currentValues["f1"],self.currentValues["Vex1"] = self.lockin1.read()
        t,self.currentValues["X2"],self.currentValues["Y2"],t,t,self.currentValues["f2"],self.currentValues["Vex2"] = self.lockin2.read()
        self.currentValues["R1"] = self.currentValues["X1"] / self.currentValues["Vex1"] * self.R_series1
        self.currentValues["R2"] = self.currentValues["X2"] / self.currentValues["Vex2"] * self.R_series2
        
    def log(self, dataToLog):
        self.logger.log(dataToLog)
        
    # A perpetual sequence
    def sequence(self):
        while True:
            yield True
        
    def finish(self):
        self.logger.finish()
        del self.lakeshore
        del self.cryocon
        del self.magnet
        del self.lockin1
        del self.lockin2


# load a csv file from Janis He-3 measurements and return the data as a dict of np arrays
def loadfile(filename): 
    with open(filename, mode="r") as f:
        reader = csv.reader(f)
        next(reader)
        datalist = []
        for var in VAR_LIST:
            datalist.append([])
        for row in reader:
            for i in range(0, len(VAR_LIST)):
                datalist[i].append(row[i])
        datadict = {}
        for i in range(0, len(VAR_LIST)):
            datadict[VAR_LIST[i]] = np.array(datalist[i], dtype=np.float_)
        return datadict
