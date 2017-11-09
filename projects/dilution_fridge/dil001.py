""" For Dilution Fridge Measurements
"""
import time, csv, math
import numpy as np

from elflab import uis, datasets
import elflab.abstracts as abstracts
import elflab.dataloggers.csvlogger as csvlogger

from elflab.devices.T_controllers.leiden import LeidenTC
from elflab.devices.lockins import stanford, signal_recovery
from elflab.devices.magnets import fake_magnets, ami



# Default path to the Leiden temperature controller exe / vi
TC_PATH = r"C:\Software\Leiden Cryogenics\TC\DR TempControl.exe\TC.vi"
# Default channel numbers of the various thermometers
TC_CERNOX = 7
TC_RUO = 8
TC_CMN = 9

# Default addresses
ADD_7124 = r"USB0::0x0A2D::0x0018::09337277::RAW"
GPIB_SR830 = 10
COM_Hx = 35
COM_Hy = 36
COM_Hz = 37


# Conversion between data names and indices and labels etc.
VAR_ORDER = ["n", "time", "T_sample", "R1", "R2", "X1", "Y1", "Vex1", "f1", "X2", "Y2", "Vex2", "f2", "T_Cernox", "T_RuO", "T_CMN", "R_Cernox", "R_RuO", "L_CMN", "Hx", "Hy", "Hz"]


VAR_TITLES = {
            "n": "n",
            "time": "t / s",
            "T_sample": "T_sample / K",
            "R1": "R1/ Ohm",
            "R2": "R2/ Ohm",
            "X1": "X1/ V",
            "Y1": "Y1 / V",
            "Vex1": "Vex / V",
            "f1": "f1 / Hz",
            "X2": "X2 / V",
            "Y2": "Y2 / V",
            "f2": "f2 / Hz",
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
            "f1": "{:.10e}",
            "X2": "{:.10e}",
            "Y2": "{:.10e}",
            "Vex2": "{:.10e}",
            "f2": "{:.10e}", 
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
    DEFAULT_FOLDER = r"D:\Dropbox (KGB Group)\Dilution_Fridge\data\test"
    DEFAULT_FN = r"test"
 
    
class Dil001TwoLockin(abstracts.ExperimentBase):
    # Pre-defined properties
    title = "Dilution Fridge 001"
    
    address_7124 = ADD_7124
    gpib_sr830 = GPIB_SR830
    address_Hx = "ASRL{:d}".format(COM_Hx)
    address_Hy = "ASRL{:d}".format(COM_Hy)
    address_Hz = "ASRL{:d}".format(COM_Hz)
    
    ch_cernox = TC_CERNOX
    ch_ruo = TC_RUO
    ch_cmn = TC_CMN
    
    default_params = {
        "sampling interval / s": "0.1",
        "R_series1 / Ohm": 'no entry',
        "R_series2 / Ohm": 'no entry',
        "which magnets": ""
    }
    param_order = [
        "which magnets",
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
        # Save parameters
        self.measurement_interval = float(params["sampling interval / s"])
        self.R_series1 = float(params["R_series1 / Ohm"])
        self.R_series2 = float(params["R_series2 / Ohm"])
        which_magnets = params["which magnets"].lower()
        
        # Initialise variables
        self.current_values = VAR_INIT.copy()
        self.var_titles = VAR_TITLES.copy()
        
        # Define the instruments
        self.leiden_tc = LeidenTC(r"C:\Software\Leiden Cryogenics\TC\DR TempControl.exe\TC.vi")
        
        self.lockin1 = signal_recovery.Model7124(self.address_7124)
        self.lockin2 = stanford.SR830(self.gpib_sr830)
        
        if "x" in which_magnets:
            self.magnet_x = ami.Model430(address_Hx)
        else:
            self.magnet_x = fake_magnets.ConstMagnet(0.0, 0.0)
        
        if "y" in which_magnets:
            self.magnet_y = ami.Model430(address_Hy)
        else:
            self.magnet_y = fake_magnets.ConstMagnet(0.0, 0.0)
        
        if "z" in which_magnets:
            self.magnet_z = ami.Model430(address_Hz)
        else:
            self.magnet_z = fake_magnets.ConstMagnet(0.0, 0.0)
        
        # create a csv logger
        self.logger = csvlogger.Logger(filename, self.var_order, self.var_titles, self.format_strings)
        
    
    def start(self):
        # Connect to instruments
        self.lockin1.connect()
        self.lockin2.connect()
        self.magnet_x.connect()
        self.magnet_y.connect()
        self.magnet_z.connect()
        
        # Reset counter and timer
        self.n = 0
        self.t0 = time.time() - time.perf_counter()
        # Start the csv logger
        self.logger.start()
        
    # Calculating sample temperature from cernox and RuO
    def calc_sample_temperature(self):
        if self.current_values["T_Cernox"] >= 20.0:
            self.current_values["T_sample"] = self.current_values["T_Cernox"]
        elif (self.current_values["T_Cernox"] <= 10.0) or (self.current_values["T_RuO"] < 8.0):
            self.current_values["T_sample"] = self.current_values["T_RuO"]
        elif (self.current_values["T_Cernox"] > 10.0) and (self.current_values["T_Cernox"] < 20.0):
            self.current_values["T_sample"] = (self.current_values["T_Cernox"] - 10.0) * self.current_values["T_Cernox"] / 10.0 + (20.0 - self.current_values["T_Cernox"]) * self.current_values["T_RuO"] / 10.0
        else:
            self.current_values["T_sample"] = float("NaN")
            
            
        
    def measure(self):
        self.current_values["n"] += 1
        self.current_values["t"] = self.t0 + time.perf_counter()
        
        _,self.current_values["T_Cernox"],self.current_values["R_Cernox"] = self.leiden_tc.read(self.ch_cernox)
        _,self.current_values["T_RuO"],self.current_values["R_RuO"] = self.leiden_tc.read(self.ch_ruo)
        
        _,self.current_values["Hx"],_ = self.magnet_x.read()
        _,self.current_values["Hy"],_ = self.magnet_y.read()
        _,self.current_values["Hz"],_ = self.magnet_z.read()
        
        _,self.current_values["X1"],self.current_values["Y1"],_,_,self.current_values["f1"],self.current_values["Vex1"] = self.lockin1.read()
        _,self.current_values["X2"],self.current_values["Y2"],_,_,self.current_values["f2"],self.current_values["Vex2"] = self.lockin2.read()
        self.current_values["R1"] = self.current_values["X1"] / self.current_values["Vex1"] * self.R_series1
        self.current_values["R2"] = self.current_values["X2"] / self.current_values["Vex2"] * self.R_series2
        
        
        _,self.current_values["T_CMN"],self.current_values["L_CMN"] = self.leiden_tc.read(self.ch_cmn)
        
        self.calc_sample_temperature()
        
    def log(self, dataToLog):
        self.logger.log(dataToLog)
        
    # A perpetual sequence
    def sequence(self):
        while True:
            yield True
        
    def finish(self):
        self.logger.finish()
        del self.leiden_tc
        del self.lockin1
        del self.lockin2
        del self.magnet_x
        del self.magnet_y
        del self.magnet_z


        
 
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
