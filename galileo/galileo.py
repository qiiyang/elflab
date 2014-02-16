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
        
    PROMPT = r"?>"
        
    # flags to be initialised
    # flag_stop = False
    # flag_quit = False
    # flag_pause = False
    # flag_plotAlive = False

    def __init__(self, experiment, measurement_interval, plotXYs, plot_refresh_interval=DEFAULT_PLOT_REFRESH_INTERVAL, plot_listen_interval=DEFAULT_PLOT_LISTEN_INTERVAL):
              # (self, experiment object, XYs for the sub-plots, ...) 
        print("    [Galileo:] Initialising Galileo......\n")
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
        
        # Initialize plotting flow
        xys = []        # the container to blow to the plotting service
        for i in range(self.NROWS):
            xys.append([])
            for j in range(self.NCOLS):
                xys[i].append([])
                for k in (0, 1):
                    xys[i][j].append(0.)
        print("    [Galileo:] Measurements have started.\n")        
        
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
        print("    [Galileo:] Measurements have been terminated. Enter \"quit\" to quit Galileo.\n")
    
    # for checking the plot status when measurements are not active
    def plotCheck(self, mainConn, pipeLock):
        while (not self.flag_quit) and (self.flag_stop or self.flag_pause):
            with pipeLock:
                # Update flag_plotAlive and empty incoming flow
                while mainConn.poll():
                    self.flag_plotAlive = mainConn.recv()                
            if (not self.flag_quit) and (self.flag_stop or self.flag_pause):
                time.sleep(self.PLOT_LISTEN_INTERVAL)
        
    def plottingProc(self, *args, **kwargs):
        pl = plot_live.PlotLive(*args, **kwargs)
        pl.start()         
        
    def start(self):
        # Start the plotting service
        print("    [Galileo:] Starting the live data plotting service......")
        plotProc = multiprocessing.Process(target=self.plottingProc, name="Galileo: Data plotting",
                                           kwargs={"plotConn": self.plotConn,
                                                   "processLock": self.procLock,
                                                   "xyVars": self.plotXYs,
                                                   "xyLabels": self.plotLabels,
                                                   "refreshInterval": self.PLOT_REFRESH_INTERVAL,
                                                   "listenInterval": self.PLOT_LISTEN_INTERVAL
                                                   }
                                           )

        plotProc.start()
        with self.pipeLock:
            while not self.mainConn.poll():
                time.sleep(self.PLOT_LISTEN_INTERVAL)
        print("    [Galileo:] Live data plotting service has started.\n\n    [Galileo:] Starting measurements......")

                    
        # Start data logging
        measureThread = threading.Thread(target=self.keepMeasuring, name="Galileo: Measurements", args=(self.mainConn, self.procLock, self.pipeLock, self.bufferLock))
        measureThread.start()
        
        # Start a dummy plotCheck thread
        checkerThread = threading.Thread(target=None)
        checkerThread.start()
        
        time.sleep(1.)
        print(self.HELP_INFO)
        
        while not self.flag_quit:
            command = input(self.PROMPT).strip().lower()
            if (command == "help") or (command == "h"):
                print(self.HELP_INFO)
            elif command == "quit":
                if not self.flag_stop:
                    print("    [Galileo:] Terminating measurements......")
                    with self.pipeLock:
                        self.flag_stop = True
                        self.mainConn.send(("stop", []))
                    measureThread.join()
                print("    [Galileo:] Terminating data plotting......")
                with self.pipeLock:
                    self.flag_quit = True
                    self.mainConn.send(("quit", []))
                plotProc.join()
                checkerThread.join()
            elif (command == "pause") or (command == "p"):
                if self.flag_stop:
                    print("    [Galileo:] WARNING: Measurements have already been permanently terminated, cannot pause!")
                else:
                    self.flag_pause = True
                    print("    [Galileo:] Measurements are paused. Enter \"resume\" to resume.")
                    # Start the bare bone plot status checker if not already on
                    if not checkerThread.is_alive():
                        checkerThread = threading.Thread(target=self.plotCheck, name="Galileo: plotCheck", args=(self.mainConn, self.pipeLock))
                        checkerThread.start()
            elif (command == "resume") or (command == "r"):
                if self.flag_stop:
                    print("    [Galileo:] WARNING: Measurements have already been permanently terminated, cannot resume!")
                else:
                    self.flag_pause = False
                    checkerThread.join()
                    print("    [Galileo:] Measurements have been resumes.")
            elif command == "stop":
                if self.flag_stop:
                    print("    [Galileo:] WARNING: Measurements have already been permanently terminated, cannot stop again!")
                else:
                    print("    [Galileo:] Terminating measurements......")
                    with self.pipeLock:
                        self.flag_stop = True
                        self.mainConn.send(("stop", []))
                    measureThread.join()
                    # Start the bare bone plot status checker if not already on
                    if not checkerThread.is_alive():
                        checkerThread = threading.Thread(target=self.plotCheck, name="Galileo: plotCheck", args=(self.mainConn, self.pipeLock))
                        checkerThread.start()
            elif not (command == ''):
                print("    [Galileo:] WARNING: Unrecognised command: \"{}\".\n".format(command))
        print("    [Galileo:] I quit, yet it moves.\n")