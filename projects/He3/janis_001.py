""" Common definitions / whatever shared for all Janis He-3 related scripts
"""
import time
import csv
import numpy as np

from elflab import uis
from elflab.devices.T_controllers.lakeshore import Lakeshore332
from elflab.devices.T_controllers.cryocon import Cryocon32B

from elflab.devices.lockins import fake_lockins, par, stanford
from elflab.devices.magnets import fake_magnets
from elflab.devices.dmms import keithley

import elflab.abstracts as abstracts
import elflab.dataloggers.csvlogger as csvlogger


GPIB_CRYOCON32B = 13
GPIB_LAKESHORE332 = 8
GPIB_DMM = 19
GPIB_SR830 = 10

# Conversion between data names and indices and labels etc.

VAR_ORDER = ["n", "t", "T_sample", "T_sorb", "T_flow", "H", "R1", "R2", "X1", "Y1", "f1", "Vex1", "X2", "Y2", "f2", "Vex2", "I_magnet"]

# Everything in SI

VAR_DESC = {
            "n": "no. of data points",
            "t": "timestamp, absolute, in s",
            "T_sample": "sample temperature / K",
            "T_sorb": "sorb temperature / K",
            "T_flow": "flow temperature / K",
            "H": "magnetic field, in T",
            "R1": "Resistance of channel 1 / Ohm",
            "R2": "Resistance of channel 2 / Ohm",
            "X1": "Lockin X on ch 1 / V", 
            "Y1": "Lockin Y on ch 1 / V",
            "f1": "Lockin frequency on ch 1 / Hz",
            "Vex1": "Lockin sine output on ch 1 / V",
            "X2": "Lockin X on ch 2 / V", 
            "Y2": "Lockin Y on ch 2 / V",
            "f2": "Lockin frequency on ch 2 / Hz",
            "Vex2": "Lockin sine output on ch 2 / V",
            "I_magnet": "Magnet current / A"
            }
            
VAR_TITLES = {
            "n": "n",
            "t": "t / s",
            "T_sample": "T_sample / K",
            "T_sorb": "T_sorb / K",
            "T_flow": "T_flow / K",
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
            "Vex2": "Vex2 / V",
            "I_magnet": "I_magnet / A"
            }
            
VAR_FORMATS = {
            "n": "{:n}",
            "t": "{:.8f}",
            "T_sample": "{:.10e}",
            "T_sorb": "{:.10e}",
            "T_flow": "{:.10e}",
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
            "Vex2": "{:.10e}",
            "I_magnet": "{:.10e}" 
            }
            
VAR_INIT = {
            "n": 0,
            "t": 0.,
            "T_sample": 0.,
            "T_sorb": 0.,
            "T_flow": 0.,
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
            "Vex2": 0.,
            "I_magnet": 0.
            }
                 

#SENS_RANGE = (0.1, 0.8)
    
class Janis001GUI(uis.GenericGUI):
    DEFAULT_FOLDER = r"D:\He3_Data\test"
    DEFAULT_FN = r"test"

 
    
class Janis001He3TwoLockinAbstract(abstracts.ExperimentBase):
    title = "Janis 001 He-3: Measurements With Two Lock In Amplifiers"
    
    default_params = {
        "R_series1 / Ohm": 'no entry',
        "R_series2 / Ohm": 'no entry',
        "sampling interval / s": "0.1"
    }
    param_order = [
        "sampling interval / s",
        "R_series1 / Ohm",
        "R_series2 / Ohm"
    ]
    
    var_order = VAR_ORDER.copy()    # order of variables
    var_titles = VAR_TITLES.copy()    # matching short names with full titles  = {e.g "H": "$H$ (T / $\mu_0$)"}
    format_strings = VAR_FORMATS.copy()   # Format strings for the variables
    
    plotXYs = [
            [("T_sample", "R1"), ("T_sample", "R2")],
            [("t", "T_sample"), ("t", "T_flow")]
            ]
    
    default_comments = ""
    
    def __init__(self, params, filename, lockin1, lockin2, magnet):
        # Define the temperature controllers
        self.cryocon = Cryocon32B(GPIB_CRYOCON32B)
        self.lakeshore = Lakeshore332(GPIB_LAKESHORE332)
        
    
        # Save parameters
        self.measurement_interval = float(params["sampling interval / s"])
        
        self.lockin1 = lockin1
        self.R_series1 = float(params["R_series1 / Ohm"])
        self.lockin2 = lockin2
        self.R_series2 = float(params["R_series2 / Ohm"])
        self.magnet = magnet
        
        # Initialise variables
        self.current_values = VAR_INIT.copy()
        self.var_titles = VAR_TITLES.copy()
        
        # create a csv logger
        self.logger = csvlogger.Logger(filename, self.var_order, self.var_titles, self.format_strings)
        
    
    def start(self):
        # Connect to instruments
        self.cryocon.connect()
        self.lakeshore.connect()
        self.lockin1.connect()
        self.lockin2.connect()
        self.magnet.connect()
        
        '''if self.lockin1.is_digital:
            self.lockin1.setAutoSens(*SENS_RANGE)
        if self.lockin2.is_digital:
            self.lockin2.setAutoSens(*SENS_RANGE)'''
        
        # Reset counter and timer
        self.n = 0
        self.t0 = time.time() - time.perf_counter()
        # Start the csv logger
        self.logger.start()
        
    def measure(self):
        self.current_values["n"] += 1
        self.current_values["t"] = self.t0 + time.perf_counter()
        t,self.current_values["T_flow"] = self.cryocon.read("A")
        t,self.current_values["T_sample"] = self.cryocon.read("B")
        t,self.current_values["T_sorb"] = self.lakeshore.read("A")
        t,self.current_values["H"],t = self.magnet.read()
        t,self.current_values["X1"],self.current_values["Y1"],_,_,self.current_values["f1"],self.current_values["Vex1"] = self.lockin1.read()
        t,self.current_values["X2"],self.current_values["Y2"],_,_,self.current_values["f2"],self.current_values["Vex2"] = self.lockin2.read()
        self.current_values["R1"] = self.current_values["X1"] / self.current_values["Vex1"] * self.R_series1
        self.current_values["R2"] = self.current_values["X2"] / self.current_values["Vex2"] * self.R_series2
        
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


class Janis001PAR124MI(Janis001He3TwoLockinAbstract):
    # "Public" Variables
    title = "Janis S07 He-3: MI measurements with PAR 124"
    
    default_params = {
        "sampling interval / s": "0.1",
        "R_series1 / Ohm": 'no entry',
        "sens / V": 'no entry',
        "theta / degrees": 'no entry',
        "f / Hz": 'no entry',
        "Vout / V": 'no entry',
        "transformer mode": '0 for False',
        "GPIB DMM": "{:d}".format(GPIB_DMM)
    }
    
    param_order = [
        "sampling interval / s",
        "GPIB DMM",
        "R_series1 / Ohm",
        "sens / V",
        "theta / degrees",
        "f / Hz",
        "Vout / V",
        "transformer mode"]
    
    var_order = VAR_ORDER.copy()    # order of variables
    var_titles = VAR_TITLES.copy()    # matching short names with full titles  = {e.g "H": "$H$ (T / $\mu_0$)"}
    format_strings = VAR_FORMATS.copy()   # Format strings for the variables
    
    plotXYs = [
            [("T_sample", "X1"), ("t", "T_sample")],
            [("t", "T_flow"), ("t", "T_sorb")]
            ]
    
    default_comments = ""
    
    def __init__(self, params, filename):   
        sens = float(params["sens / V"])
        theta = float(params["theta / degrees"])
        f = float(params["f / Hz"])
        Vout = float(params["Vout / V"])
        transformer = (int(params["transformer mode"]) != 0)
        
        gpib_dmm = int(params["GPIB DMM"])
        
        dmm = keithley.Keithley196(gpib_dmm)
        lockin1 = par.PAR124A(dmm, sens=sens, theta=theta, f=f, Vout=Vout, transformer=transformer)
        lockin2 = fake_lockins.ConstLockin(float("nan"))
        
        magnet = fake_magnets.ConstMagnet()
        
        p = params.copy()
        p["R_series2 / Ohm"] = "0"
        super().__init__(p, filename, lockin1, lockin2, magnet)
   
   

class Janis001SR830PAR124(Janis001He3TwoLockinAbstract):
    # "Public" Variables
    title = "Janis S07 He-3: SR830 & PAR124"
    
    default_params = {
        "sampling interval / s": "0.1",
        "SR830 GPIB": "{:d}".format(GPIB_SR830),
        "SR830 R_series / Ohm": "no entry",
        "PAR124 DMM GPIB": "{:d}".format(GPIB_DMM),
        "PAR124 R_series / Ohm": 'no entry',
        "PAR124 sens / V": 'no entry',
        "PAR124 theta / degrees": 'no entry',
        "PAR124 f / Hz": 'no entry',
        "PAR124 Vout / V": 'no entry',
        "PAR124 transformer mode": '0 for False'
    }
    
    param_order = [
        "sampling interval / s",
        "SR830 GPIB",
        "SR830 R_series / Ohm",
        "PAR124 DMM GPIB",
        "PAR124 R_series / Ohm",
        "PAR124 sens / V",
        "PAR124 theta / degrees",
        "PAR124 f / Hz",
        "PAR124 Vout / V",
        "PAR124 transformer mode"]
    
    var_order = VAR_ORDER.copy()    # order of variables
    var_titles = VAR_TITLES.copy()    # matching short names with full titles  = {e.g "H": "$H$ (T / $\mu_0$)"}
    format_strings = VAR_FORMATS.copy()   # Format strings for the variables
    
    plotXYs = [
            [("T_sample", "R1"), ("T_sample", "R2")],
            [("t", "T_flow"), ("t", "T_sample")]
            ]
    
    default_comments = ""
    
    def __init__(self, params, filename):   
        gpib_sr830 = int(params["SR830 GPIB"])
        lockin1 = stanford.SR830(gpib_sr830)
        
        sens = float(params["PAR124 sens / V"])
        theta = float(params["PAR124 theta / degrees"])
        f = float(params["PAR124 f / Hz"])
        Vout = float(params["PAR124 Vout / V"])
        transformer = (int(params["PAR124 transformer mode"]) != 0)
        
        gpib_dmm = int(params["PAR124 DMM GPIB"])
        dmm = keithley.Keithley196(gpib_dmm)
        lockin2 = par.PAR124A(dmm, sens=sens, theta=theta, f=f, Vout=Vout, transformer=transformer)
        
        magnet = fake_magnets.ConstMagnet()
        
        p = params.copy()
        p["R_series1 / Ohm"] = params["SR830 R_series / Ohm"]
        p["R_series2 / Ohm"] = params["PAR124 R_series / Ohm"]
        
        super().__init__(p, filename, lockin1, lockin2, magnet)
   
   
# load a csv file from Janis He-3 measurements and return the data as a dict of np arrays
def loadfile(filename): 
    with open(filename, mode="r") as f:
        reader = csv.reader(f)
        next(reader)
        datalist = []
        for var in VAR_ORDER:
            datalist.append([])
        for row in reader:
            for i in range(0, len(row)):
                datalist[i].append(float(row[i]))
            # For backward compatibility #
            for i in range(len(row), len(VAR_ORDER)):
                datalist[i].append(float('nan'))
        datadict = {}
        for i in range(0, len(VAR_ORDER)):
            datadict[VAR_ORDER[i]] = np.array(datalist[i], dtype=np.float_)
        return datadict
