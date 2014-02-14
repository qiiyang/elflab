""" The main script to run the measurements with a mutual inductance probe
"""

DEBUG_INFO = False

# Parameters to be set by the user for each measurement
# ____Measurement Parameters
INTERVAL = 0.001    # interval between single measurements, in s
THERMOMETER = ("devices.thermometers.fake_therms", "StepTherm")
                # (module, class) of the instrument
LOCKIN = (r"devices.lockins.fake_lockins", "SinCosLockin")
MAGNET = (r"devices.magnets.fake_magnets", "StepMagnet")

# ____Plot Parameters
NROWS = 2   # number of rows of sub plots
NCOLS = 1   # number of columns of sub plots
PLOTFPS = 100
XYVARS = [
            [("n", "X")],
            [("n", "Y")]
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
    xys = []        # plotting buffer
    for i in range(NROWS):
        xys.append([])
        for j in range(NCOLS):
            xys[i].append([])
            for k in (0, 1):
                xys[i][j].append(0.)    
                
    # ____Initialise clock and counter
    time.perf_counter()
    n = 0
    
    # Measure
    while not flag_quit:
        if not flag_pause:
            buffer = once.measure(buffer, therm, magnet, lockin)
            buffer["n"] = n
            n += 1
            if pipeEnd.poll():
                for i in range(NROWS):
                    for j in range(NCOLS):
                        for k in (0, 1):
                            xys[i][j][k] = buffer[XYVARS[i][j][k]]
                while pipeEnd.poll():
                    pipeEnd.recv()  # clearing receiving pipe
                pipeEnd.send(xys)
        if not flag_quit:
            time.sleep(INTERVAL)
    
    print("[Galileo: ] Measurements terminated by user.")

# Data Plotting Process
def plottingProc(processLock, pipeEnd, nrows, ncols, xyLabels, plot_interval):
    import plots.plot_live as plot
    pl = plot.PlotLive(pipeEnd, nrows, ncols, xyLabels, plot_interval)
    pl.start()
    
# The main procedure
if __name__ == '__main__':

    # Global variables
    flag_pause = False
    flag_quit = False
    
    end1, end2 = multiprocessing.Pipe()
    processLock = multiprocessing.RLock()
    threadLock = threading.RLock()
    
    # Calculate axes labels
    xyLabels = []
    for i in range(NROWS):
        xyLabels.append([])
        for j in range(NCOLS):
            xyLabels[i].append([])
            for k in (0, 1):
                xyLabels[i][j].append(mi.dataLabels[XYVARS[i][j][k]])

    # Start data logging
    thread = threading.Thread(target=keepMeasuring, name="LabPy: Data logging", args=(processLock, threadLock, end1))
    thread.start()
    
    # Start plotting
    proc = multiprocessing.Process(target=plottingProc, name="LabPy: Data plotting", args=(processLock, end2, NROWS, NCOLS, xyLabels, 1000./PLOTFPS))
    proc.start()
    
    time.sleep(3.)
    while not flag_quit:
        command = input(r"Galileo listening> ",).strip().lower()
        
        if (command == "quit") or (command == "q"):
            flag_quit = True
        elif (command == "pause") or (command == "p"):
            flag_pause == True
        elif (command == "resume") or (command == "r"):
            flag_pause == False
            
    
    # Waiting to finish
    thread.join()
    proc.join()
    
    print("[Galileo: ] User closed graph window. Galileo quits.")