""" The main script to run the measurements with a mutual inductance probe
"""

DEBUG_INFO = False

# Parameters to be set by the user for each measurement
# ____Measurement Parameters
MEASUREMENT_PERIOD = 0.001    # interval between single measurements, in s
THERMOMETER = ("devices.thermometers.fake_therms", "StepTherm")
                # (module, class) of the instrument
LOCKIN = (r"devices.lockins.fake_lockins", "SinCosLockin")
MAGNET = (r"devices.magnets.fake_magnets", "StepMagnet")

# ____Plot Parameters
NROWS = 2   # number of rows of sub plots
NCOLS = 1   # number of columns of sub plots
PLOT_REFRESH_PERIOD = 0.5     # Interval between plot refreshes
PLOT_LISTEN_PERIOD = 0.003    # Interval between listening events

XYVARS = [
            [("n", "X")],
            [("n", "Y")]
         ]      # Names of variable pairs to plot in each sub-plot
            
# Set search paths
import sys
import os
# _____Find LabPy root path and add to search path
galileoPath = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, galileo)
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
    while not flag_stop:
        if not flag_pause:
            buffer = once.measure(buffer, therm, magnet, lockin)
            buffer["n"] = n
            n += 1
            
            # Send data for plotting
            with threadLock:        # Prevent other threads from accessing the pipe
                if pipeEnd.poll():
                    while pipeEnd.poll():
                        flag_plotAlive=pipeEnd.recv()
                    for i in range(NROWS):
                        for j in range(NCOLS):
                            for k in (0, 1):
                                xys[i][j][k] = buffer[XYVARS[i][j][k]]
                    pipeEnd.send(("data", xys))
        if not flag_stop:
            time.sleep(MEASUREMENT_PERIOD)
    print("    [Galileo:] You terminated the measurements. Type \"quit\" to quit Galileo.\n")

# Data Plotting Process
def plottingProc(processLock, pipeEnd, nrows, ncols, xyVars, xyLabels, listenPeriod, refreshPeriod):
    import plots.plot_live as plot
    pl = plot.PlotLive(processLock, pipeEnd, nrows, ncols, xyVars, xyLabels, listenPeriod, refreshPeriod)
    pl.start()
    
# The main procedure
if __name__ == '__main__':

    # Global variables
    flag_pause = False
    flag_stop = False
    flag_quit = False
    flag_replot = False
    flag_autoscale = True
    flag_plotAlive = False
    
    n_plotPoints = 0
    
    endMain, endPlot = multiprocessing.Pipe()   # Pipe for inter-process communications
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

    # Start the plotting service
    plotProc = multiprocessing.Process(target=plottingProc, name="Galileo: Data plotting", args=(processLock, endPlot, NROWS, NCOLS, XYVARS, xyLabels, PLOT_LISTEN_PERIOD, PLOT_REFRESH_PERIOD))
    plotProc.start()
                
    # Start data logging
    measureThread = threading.Thread(target=keepMeasuring, name="Galileo: Data logging", args=(processLock, threadLock, endMain))
    measureThread.start()
    
    time.sleep(1.)
    print("""\
    *************** Galileo Measurement Utility ***********************
    'Measure what is measurable, and make measurable what is not so.'
                                                --- Galileo Galilei
    *******************************************************************

Available commands:
            "pause"     or  "p":        Pause the measurements (CAN
                                        resume later).

            "resume"    or  "r":        Resume the measurements.

            "stop"      or  "s":        Stop the measurements (can NOT
                                        resume later), while keeping
                                        the graph available.

            "quit"      or  "q"         Quit Galileo and return to com-
                                        mand line console.

            Ctrl+Break                  Force quit.
                                        
Type a command after the prompt "?>", and press "Enter" to execute.
    """)
    while not flag_quit:
        command = input(r"?> ",).strip().lower()
        if (command == "stop") or (command == "s"):
            with threadLock:
                flag_stop = True
                endMain.send(("stop", []))
            measureThread.join()
        elif (command == "quit") or (command == "q"):
            if not flag_stop:
                with threadLock:
                    flag_stop = True
                    endMain.send(("stop", []))
                measureThread.join()           
            with threadLock:
                flag_quit = True
                endMain.send(("quit", []))
            plotProc.join()
        elif (command == "pause") or (command == "p"):
            flag_pause = True
        elif (command == "resume") or (command == "r"):
            flag_pause = False
        elif not (command == ''):
            print("    [Galileo:] WARNING: Unrecognised command: \"{}\".\n".format(command))

    print("    [Galileo:] And yet it moves.\n")