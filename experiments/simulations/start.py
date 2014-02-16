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
            [("n", "X")],
            [("n", "Y")]
         ]      # Names of variable pairs to plot in each sub-plot
            

    
# Import other modules
import importlib
import time
import elflab.galileo.galileo as galileo
import mi_common as mi

    
class SimMI(galileo.AbstractExperiment):
    def __init__(self):
        self.buffer = mi.initialData.copy()
        self.dataLabels = mi.dataLabels
        self.n = 0
        time.perf_counter()
        ThermClass = getattr(importlib.import_module(THERMOMETER[0]), THERMOMETER[1])
        self.therm = ThermClass()
        
        MagnetClass = getattr(importlib.import_module(MAGNET[0]), MAGNET[1])
        self.magnet = MagnetClass()
        
        LockinClass = getattr(importlib.import_module(LOCKIN[0]), LOCKIN[1])
        self.lockin = LockinClass()
        
    def measure(self):
        self.buffer["n"] += 1
        self.buffer["t"] = time.perf_counter()
        (self.buffer["I_therm"], self.buffer["V_therm"], self.buffer["T"]) = self.therm.read()
        (self.buffer["I_mag"], self.buffer["H"]) = self.magnet.read()
        (self.buffer["X"], self.buffer["Y"]) = self.lockin.readXY()
        
    def log(self):
        pass
   
    def terminate(self):
        pass
    
# The main procedure
if __name__ == '__main__':
    sim = SimMI()
    gali = galileo.Galileo(experiment=sim, measurement_interval=MEASUREMENT_PERIOD, plotXYs=XYVARS)
    gali.start()