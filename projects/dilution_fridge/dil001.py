""" For Dilution Fridge Measurements
"""
import time
import csv
import numpy as np

from elflab import uis, datasets
from elflab.devices.T_controllers.leiden import LeidenTC

from elflab.devices.lockins import stanford

import elflab.abstracts as abstracts
import elflab.dataloggers.csvlogger as csvlogger


# path to the Leiden temperature controller exe / vi
TC_PATH = r"C:\Software\Leiden Cryogenics\TC\DR TempControl.exe\TC.vi"
# Channel numbers of the various thermometers
TC_CERNOX = 7
TC_RUO = 8
TC_CMN = 9


# Conversion between data names and indices and labels etc.
VAR_ORDER = ["n", "time", "T_sample", "R1", "R2", "X1", "Y1", "Vex1", "X2", "Y2", "Vex2", "T_Cernox", "T_RuO", "T_CMN", "R_Cernox", "R_RuO", "L_CMN", "Hx", "Hy", "Hz"]

# Everything in SI
            
VAR_TITLES = {
            "n": "n",
            "time": "t / s",
            "T_sample": "T_sample / K",
            "R1": "R1/ Ohm",
            "R2": "R2/ Ohm",
            "X1": "X1/ V",
            "Y1": "Y1 / V",
            "Vex1": "Vex / V",
            "X2": "X2 / V",
            "Y2": "Y2 / V",
            "Vex2": "Vex2 / V", 
            "T_Cernox": "T_Cernox / K",
            "T_RuO": "T_RuO / K",
            "T_CMN": "T_CMN / K",
            "R_Cernox": "R_Cernox / K",
            "R_RuO": "R_RuO / K",
            "L_CMN": "L_CMN / uH",
            "Hx": "Hx / T",
            "Hy": "Hy / T",
            "Hz": "Hz / T"
            }
            
VAR_FORMATS = {
            "n": "{:n}",
            "time": "{:.8f}",
            "T_sample": "{:.10e}",
            "R1": "{:.10e}",
            "R2": "{:.10e}",
            "X1": "{:.10e}",
            "Y1": "{:.10e}",
            "Vex1": "{:.10e}",
            "X2": "{:.10e}",
            "Y2": "{:.10e}",
            "Vex2": "{:.10e}", 
            "T_Cernox": "{:.10e}",
            "T_RuO": "{:.10e}",
            "T_CMN": "{:.10e}",
            "R_Cernox": "{:.10e}",
            "R_RuO": "{:.10e}",
            "L_CMN": "{:.10e}",
            "Hx": "{:.10e}",
            "Hy": "{:.10e}",
            "Hz": "{:.10e}"
            }
            
VAR_INIT = {
            "n": 0,
            "time": float("NaN"),
            "T_sample": float("NaN"),
            "R1": float("NaN"),
            "R2": float("NaN"),
            "X1": float("NaN"),
            "Y1": float("NaN"),
            "Vex1": float("NaN"),
            "X2": float("NaN"),
            "Y2": float("NaN"),
            "Vex2": float("NaN"), 
            "T_Cernox": float("NaN"),
            "T_RuO": float("NaN"),
            "T_CMN": float("NaN"),
            "R_Cernox": float("NaN"),
            "R_RuO": float("NaN"),
            "L_CMN": float("NaN"),
            "Hx": float("NaN"),
            "Hy": float("NaN"),
            "Hz": float("NaN")
            }
                 

#SENS_RANGE = (0.1, 0.8)
    
class Dil_GUI_Prototype(uis.GenericGUI):
    DEFAULT_FOLDER = r"C:\Dropbox (KGB Group)\Dilution_Fridge\data\test"
    DEFAULT_FN = r"test"
 
    
class Dil001TwoLockin(abstracts.ExperimentBase):
    title = "Dilution Fridge 001"
    
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
            ]
    
    default_comments = ""
    
    def __init__(self, params, filename):
        # Define the temperature controllers
        self.leiden_tc = LeidenTC(r"C:\Software\Leiden Cryogenics\TC\DR TempControl.exe\TC.vi")
    
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
        t,self.current_values["H"],self.current_values["I_magnet"] = self.magnet.read()
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
            datadict[VAR_ORDER[i]] = np.array(datalist[i], dtype=np.float_, copy=True)
        return datasets.DataSet(datadict)
