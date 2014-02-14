""" The main script to run the measurements with a mutual inductance probe
"""

DEBUG_INFO = False

# Parameters to be set by the user for each measurement
# ____Measurement Parameters
INTERVAL = 0.001    # interval between single measurements, in s
THERMOMETER = ("devices.thermometers.fake_thermometers", "StepTherm")
                # (module, class) of the instrument
LOCKIN = (r"devices.lockins.fake_lockins", "SinCosLockin")
MAGNET = (r"devices.magnets.fake_magnets", "StepMagnet")

# ____Plot Parameters
NROWS = 2   # number of rows of sub plots
NCOLS = 1   # number of columns of sub plots
XYVARS = [
            [("T", "X")],
            [("T", "Y")]
         ]      # Names of variable pairs to plot in each sub-plot
            
# Set search paths
import sys
import os
# _____Find LabPy root path and add to search path
labPyPath = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, labPyPath)
if DEBUG_INFO:
    print ("-------------------------\n##### Debug Info 1 #####\nsys.path =\n   {}\n-------------------------\n".format(sys.path))
    
# Import other modules
import mi_common as mi
import importlib
import time
import threading
import multiprocessing
import measure_once_async as once

# Global variables
flag_pause = False
flag_quit = False

# Data collection with thread
def keepMeasuring(processLock, threadLock, pipeEnd):
    # Initialise
    # ____Initialise Instruments
    ThermClass = getattr(importlib.import_module(THERMOMETER[0]), THERMOMETER[1])
    therm = ThermClass()
    
    MagnetClass = getattr(importlib.import_module(MAGNET[0]), MAGNET[1])
    magnet = MagnetClass()
    
    LockinClass = getattr(importlib.import_module(LOCKIN[0]), LOCKIN[1])
    lockin = LockinClass()
    
    # ____Initialise data buffers
    buffer = mi.initialData.copy()      # Measurement buffer
    xys = [[[0., 0.]] * NCOLS] * NROWS        # plotting buffer
    
    # ____Initialise clock
    time.perf_counter()
    
    while not flag_quit:
        while not (flag_quit or flag_pause):
            buffer = 
        time.sleep(INTERVAL)
    
    print("Measurements terminated by user.")
    