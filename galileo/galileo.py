""" Class definition of the Galileo utility
    written for Python 3.3.4
"""
# Imports
import os
import time
import multiprocessing
import threading
from ..plots import plot_live

# Default values for timing parameters
# MEASUREMENT_INTERVAL = 0.001    # interval between single measurements, in s

# Caller can omit plotting timings, by using these default
DEFAULT_PLOT_REFRESH_INTERVAL = 0.5     # Interval between plot refreshes in s
DEFAULT_PLOT_LISTEN_INTERVAL = 0.05    # Interval between listening events in s

# Default measurable lists
# DEFAULT_dataNames = ["t", "n"]
# DEFAULT_dataUnits = ["s", ""]

# Default sub-plots, defined as pairs of ("x", "y")
# DEFULT_xyNames = [("t", "n")]

class AbstractExperiment:
    """Abstract / Base defining an experiment
    An Experiment class should completely define the quantities to be measure and the measuring procedure.
    """
    # minimum variables to be override by initialiser:
    buffer = None   # = {"name": "value"}
    dataLabels = None    # = {e.g "H": "$H$ (T / $\mu_0$)"}
    
    def __init__(self):
        raise Exception("!!Galileo ERROR!! Experiment initialisation not implemented!!!")
    
    def measure(self):  # Trigger a measurement
        raise Exception("!!Galileo ERROR!! Measurement triggering method not implemented!!!")
        
    def log(self, bufferLock):  # Write the data to storage; bufferLock is a thread-level Lock object (not RLock)
        raise Exception("!!Galileo ERROR!! Data logging method not implemented!!!")
        
    def terminate(self):   # To be executed when measurements are terminated, for closing files etc
        raise Exception("!!Galileo ERROR!! Measurement termination not implemented!!!")
        
        

class Galileo:
    """The Galileo Measurement Utility"""
    # Static constants
    # ____Help information
    with open(os.path.join(os.path.dirname(__file__), "help_info.txt"), "r") as insFile:
        HELP_INFO = insFile.read()
        
    # flags to be initialised
    # flag_stop = False
    # flag_quit = False
    # flag_pause = False
    # flag_plotAlive = False

    def __init__(self, experiment, measurement_interval, plotXYs, plot_refresh_interval=DEFAULT_PLOT_REFRESH_INTERVAL, plot_listen_interval=DEFAULT_PLOT_LISTEN_INTERVAL):
              # (self, experiment object, XYs for the sub-plots, ...) 
        # set flags
        self.flag_stop = False
        self.flag_quit = False
        self.flag_pause = False
        
        self.flag_plotAlive = False
        self.flag_replot = False
        
        # save the "constants"
        self.experiment = experiment
        
        # ____the timing "constants", all in seconds
        self.MEASUREMENT_INTERVAL = measurement_interval
        self.PLOT_REFRESH_INTERVAL = plot_refresh_interval
        self.PLOT_LISTEN_INTERVAL = plot_listen_interval
        
        # Save and calculate plotting informations
        self.NROWS = len(plotXYs)
        self.NCOLS = len(plotXYs[0])
        
        self.plotXYs = plotXYs
        plotLabels = []
        for i in range(self.NROWS):
            plotLabels.append([])
            for j in range(self.NCOLS):
                plotLabels[i].append([])
                for k in (0, 1):
                    plotLabels[i][j].append(experiment.dataLabels[plotXYs[i][j][k]])
        self.plotLabels = plotLabels
        
        # initialize the pipes and locks
        self.mainConn, self.plotConn = multiprocessing.Pipe()
        self.pipeLock = threading.RLock()
        self.bufferLock = threading.RLock()
        self.procLock = multiprocessing.RLock()
       
       
    def keepMeasuring(self, mainConn, procLock, pipeLock, bufferLock):
        # Start and finish a dummy thread
        logThread = threading.Thread(target=None)
        logThread.start()
        
        # Initialize plotting buffer
        xys = []        # plotting buffer
        for i in range(self.NROWS):
            xys.append([])
            for j in range(self.NCOLS):
                xys[i].append([])
                for k in (0, 1):
                    xys[i][j].append(0.)
                    
        while not self.flag_stop:
            if not self.flag_pause:
            
                with bufferLock:
                    self.experiment.measure()   # Take a measurement
                
                # Wait for any data logging to finish
                logThread.join()
                
                # start another logging thread
                logThread = threading.Thread(target=self.experiment.log(), name="Galileo:data-logging")
                logThread.start()
                
                # Blow data to the plotting service only if requested
                with pipeLock:
                    if mainConn.poll():
                        # Update flag_plotAlive and empty incoming flow
                        while mainConn.poll():
                            self.flag_plotAlive = mainConn.recv()
                        # Blow data
                        for i in range(self.NROWS):
                            for j in range(self.NCOLS):
                                for k in (0, 1):
                                    xys[i][j][k] = self.experiment.buffer[self.plotXYs[i][j][k]]
                        mainConn.send(("data", xys))
            # Wait if not stopping    
            if not self.flag_stop:
                time.sleep(self.MEASUREMENT_INTERVAL)
                
        # Now the flag_stop must have been triggered, finishing up
        logThread.join()
        self.experiment.terminate()  # Finish up any loose ends
        print("    [Galileo:] You terminated the measurements. Type \"quit\" to quit Galileo.\n")    
        
    def plottingProc(self, *args, **kwargs):
        pl = plot_live.PlotLive(*args, **kwargs)
        pl.start()         
        
    def start(self):
        # Start the plotting service
        plotProc = multiprocessing.Process(target=self.plottingProc, name="Galileo: Data plotting",
                                           kwargs={"plotConn": self.plotConn,
                                                   "processLock": self.procLock,
                                                   "xyVars": self.plotXYs,
                                                   "xyLabels": self.plotLabels,
                                                   "refreshInterval": self.PLOT_REFRESH_INTERVAL,
                                                   "listenInterval": self.PLOT_LISTEN_INTERVAL}
                                           )

        plotProc.start()
                    
        # Start data logging
        measureThread = threading.Thread(target=self.keepMeasuring, name="Galileo: Measurements", args=(self.mainConn, self.procLock, self.pipeLock, self.bufferLock))
        measureThread.start()
        
        time.sleep(1.)
        print(self.HELP_INFO)
        
        while not self.flag_quit:
            command = input(r"?> ",).strip().lower()
            if (command == "stop") or (command == "s"):
                with self.pipeLock:
                    self.flag_stop = True
                    self.mainConn.send(("stop", []))
                measureThread.join()
            elif (command == "quit") or (command == "q"):
                if not self.flag_stop:
                    with self.pipeLock:
                        self.flag_stop = True
                        self.mainConn.send(("stop", []))
                    measureThread.join()           
                with self.pipeLock:
                    self.flag_quit = True
                    self.mainConn.send(("quit", []))
                plotProc.join()
            elif (command == "pause") or (command == "p"):
                flag_pause = True
            elif (command == "resume") or (command == "r"):
                flag_pause = False
            elif not (command == ''):
                print("    [Galileo:] WARNING: Unrecognised command: \"{}\".\n".format(command))

        print("    [Galileo:] I quit, yet it moves.\n")