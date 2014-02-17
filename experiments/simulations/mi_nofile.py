""" The main script to run the measurements with a mutual inductance probe
"""

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
            

    
# Import other modules
import importlib
import time
import elflab.galileo.galileo as galileo
import elflab.galileo.model_experiments as modelexp
import mi_common as mi

class NullLogger(modelexp.LoggerBase):
    """A minimal abstraction of data-logging"""
    def __init__(self):
        pass
    
    def log(self, dataPoint):  # To write down a data point
        pass
        
    def finish(self):
        pass

class SimMIMeasurer(modelexp.MeasurerBase):
    def __init__(self):
        self.dataPoint = mi.initialData.copy()
        self.namesAndUnits = mi.dataLabels
        self.n = 0
        time.perf_counter()
        ThermClass = getattr(importlib.import_module(THERMOMETER[0]), THERMOMETER[1])
        self.therm = ThermClass()
        
        MagnetClass = getattr(importlib.import_module(MAGNET[0]), MAGNET[1])
        self.magnet = MagnetClass()
        
        LockinClass = getattr(importlib.import_module(LOCKIN[0]), LOCKIN[1])
        self.lockin = LockinClass()
        
    def measure(self):
        self.dataPoint["n"] += 1
        self.dataPoint["t"] = time.perf_counter()
        (self.dataPoint["I_therm"], self.dataPoint["V_therm"], self.dataPoint["T"]) = self.therm.read()
        (self.dataPoint["I_mag"], self.dataPoint["H"]) = self.magnet.read()
        (self.dataPoint["X"], self.dataPoint["Y"]) = self.lockin.readXY()
        
    def finish(self):
        pass
    
# The main procedure
if __name__ == '__main__':
    measurer = SimMIMeasurer()
    logger = NullLogger()
    sim = modelexp.MeasurerAndLogger("MI Simulator (No File)", measurer, logger)
    gali = galileo.Galileo(experiment=sim, measurement_interval=MEASUREMENT_PERIOD, plotXYs=XYVARS)
    gali.start()