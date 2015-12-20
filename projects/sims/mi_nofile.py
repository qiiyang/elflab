""" The main script to run the measurements with a mutual inductance probe
"""
# Import other modules
import importlib
import time
from elflab import abstracts
from elflab.dataloggers import nologger
import elflab.projects.sims.mi_common as mi

DEBUG_INFO = False

# Parameters to be set by the user for each measurement
# ____Measurement Parameters
MEASUREMENT_PERIOD = 0.001    # interval between single measurements, in s
THERMOMETER = ("elflab.devices.thermometers.fake_therms", "StepTherm")
                # (module, class) of the instrument
LOCKIN = (r"elflab.devices.lockins.fake_lockins", "SinCosLockin")
MAGNET = (r"elflab.devices.magnets.fake_magnets", "StepMagnet")

# ____Plot Parameters
NROWS = 2   # number of rows of sub plots
NCOLS = 1   # number of columns of sub plots
PLOT_REFRESH_PERIOD = 0.5     # Interval between plot refreshes
PLOT_LISTEN_PERIOD = 0.003    # Interval between listening events

XYVARS = [
            [("t", "X")],
            [("t", "Y")]
         ]      # Names of variable pairs to plot in each sub-plot
            

class SimMI(abstracts.ExperimentWithLogger):
    title = "simulated MI"
    
    param_list = ["sample_interval"]
    
    def __init__(self, params={"sample_interval":0.1}):
        self.measurement_interval = float(params["sample_interval"])
        self.currentValues = mi.initialData.copy()
        self.varTitles = mi.dataLabels
        self.plotXYs = XYVARS
        self.n = 0
        time.perf_counter()
        ThermClass = getattr(importlib.import_module(THERMOMETER[0]), THERMOMETER[1])
        self.therm = ThermClass()
        
        MagnetClass = getattr(importlib.import_module(MAGNET[0]), MAGNET[1])
        self.magnet = MagnetClass()
        
        LockinClass = getattr(importlib.import_module(LOCKIN[0]), LOCKIN[1])
        self.lockin = LockinClass()
        
        self.logger = nologger.Logger()
        
    def measure(self):
        self.currentValues["n"] += 1
        self.currentValues["t"] = time.perf_counter()
        (t, self.currentValues["I_therm"], self.currentValues["V_therm"], self.currentValues["T"]) = self.therm.read()
        (t, self.currentValues["I_mag"], self.currentValues["H"]) = self.magnet.read()
        (self.currentValues["X"], self.currentValues["Y"]) = self.lockin.readXY()
        
    def finish(self):
        pass
        
    def start(self):
        pass
        
    def sequence(self):
        while True:
            yield True
