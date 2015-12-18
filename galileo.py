""" Class definition of the Galileo utility
    Handles coordinating parallelism of measurements, controlling, data-loggin etc.
    written for Python 3.3.4
"""

# Imports
import os
import time
import multiprocessing
import threading
import random
from elflab.plotters import plot_live
import elflab.ui

# Constants

# ____Caller can omit plotting timings, by using these default
DEFAULT_PLOT_REFRESH_INTERVAL = 0.5     # Interval between plot refreshes in s
DEFAULT_PLOT_LISTEN_INTERVAL = 0.05    # Interval between listening events in s

# Default measurable lists
# DEFAULT_dataNames = ["t", "n"]
# DEFAULT_dataUnits = ["s", ""]

# Default sub-plots, defined as pairs of ("x", "y")
# DEFULT_xyNames = [("t", "n")]

class Galileo:
    """The Galileo Measurement Utility"""
    # Default "static constants"
    PROMPT = r"?>"
    UI_LAG = 0.3
    # ____Help information
    with open(os.path.join(os.path.dirname(__file__), "misc", "galileo_help_info.txt"), "r") as inpFile:
        HELP_INFO = inpFile.read()
    QUESTIONS = []
    with open(os.path.join(os.path.dirname(__file__), "misc", "galileo_questions.txt"), "r") as inpFile:
        for line in inpFile:
            QUESTIONS.append(line.strip())
      
        
    # flags to be initialised
    # flag_stop = False
    # flag_quit = False
    # flag_pause = False
    # flag_plotAlive = False

    def __init__(self, experiment, measurement_interval, plotXYs, plot_refresh_interval=DEFAULT_PLOT_REFRESH_INTERVAL, plot_listen_interval=DEFAULT_PLOT_LISTEN_INTERVAL):
              # (self, Experiment object, XYs for the sub-plots, ...) 
        print("    [Galileo:] Initialising Galileo......")
        # set flags
        self.flag_stop = False
        self.flag_quit = False
        self.flag_pause = False
        
        # save the variables
        self.experiment = experiment
        
        # ____the timing "constants", all in seconds
        self.measurement_interval = measurement_interval
        self.plot_refresh_interval = plot_refresh_interval
        self.plot_listen_interval = plot_listen_interval
        
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
                    plotLabels[i][j].append(experiment.varTitles[plotXYs[i][j][k]])
        self.plotLabels = plotLabels
        
        # initialize the pipes and locks
        self.plotConn, self.mainConn = multiprocessing.Pipe(duplex=False)
        self.pipeLock = threading.RLock()
        self.dataLock = threading.RLock()
        self.processLock = multiprocessing.RLock()
        
        # Initialise RNG
        random.seed()
       
       
    def keepMeasuring(self, mainConn, processLock, pipeLock, dataLock):
        # Start and finish a dummy thread
        logThread = threading.Thread(target=None)
        logThread.start()
        
        # Initialize plotting data
        xys = []        # the container to blow to the plotting service
        for i in range(self.NROWS):
            xys.append([])
            for j in range(self.NCOLS):
                xys[i].append([])
                for k in (0, 1):
                    xys[i][j].append(0.)        
        
        # Measure
        for token in self.experiment.sequence():
            if not self.flag_stop:
                with dataLock:
                    self.experiment.measure()   # Take a measurement
                
                # Wait for any data logging to finish
                logThread.join()
                
                # start another logging thread
                with dataLock:
                    dataToLog = self.experiment.currentValues.copy()
                logThread = threading.Thread(target=self.experiment.log, name="Galileo:data-logging", kwargs={"dataToLog":dataToLog})
                logThread.start()
                
                # Blow data to the plotting service only if requested
                if self.plotStatus["request_data"].is_set():
                    # Blow data
                    for i in range(self.NROWS):
                        for j in range(self.NCOLS):
                            for k in (0, 1):
                                xys[i][j][k] = self.experiment.currentValues[self.plotXYs[i][j][k]]
                    with pipeLock:
                        mainConn.send(("data", xys))
                    self.plotStatus["request_data"].clear()
            # Pause if asked to
            while self.flag_pause and not self.flag_stop:
                time.sleep(self.measurement_interval)
            # Check whether to stop now.
            if self.flag_stop:
                break
            else:
                time.sleep(self.measurement_interval)
                
        # Now the flag_stop must have been triggered, finishing up
        logThread.join()
        self.experiment.finish()  # Finish up any loose ends
        # Print messages
        print("\n    [Galileo:] Measurements have been terminated. Enter \"quit\" to quit Galileo.\n")
        self.prompt()
        
        
    def plottingProc(self, *args, **kwargs):
        pl = plot_live.PlotLive(*args, **kwargs)
        pl.start()         
    
    def help(self):
        print(self.HELP_INFO)
        self.prompt()
    
    def pause(self):
        if self.flag_stop:
            print("    [Galileo:] WARNING: Measurements have already been permanently terminated, cannot pause!")
        else:
            self.flag_pause = True
            print("    [Galileo:] Measurements are paused. Enter \"resume\" to resume.")
        self.prompt()
            
    def resume(self):
        if self.flag_stop:
            print("    [Galileo:] WARNING: Measurements have already been permanently terminated, cannot resume!")
        else:
            self.flag_pause = False
            print("    [Galileo:] Measurements have been resumes.")
        self.prompt()
            
    def stop(self):
        if self.flag_stop:
            print("    [Galileo:] WARNING: Measurements have already been permanently terminated, cannot stop again!")
            self.prompt()
        else:
            print("    [Galileo:] Terminating measurements......")
            self.flag_stop=True
            self.measureThread.join()
    
    def quit(self):
        print("a\n")
        if not self.flag_stop:
            print("    [Galileo:] Terminating measurements......")
            self.flag_stop = True
            self.measureThread.join()
        print("    [Galileo:] Terminating data plotting......\n")
        with self.pipeLock:
            self.flag_quit = True
            self.mainConn.send(("quit", []))
        self.plotProc.join(3)
        if self.plotProc.is_alive():
            print("    [Galileo:] WARNING: Data plotting time-out, forcibly terminating......\n")
            with self.pipeLock:
                self.plotProc.terminate()
        print("    [Galileo:] Live plotting service is terminated.\n")
        print("    [Galileo:] Yet it moves.\n") 
        
    def plot(self):
        if self.plotStatus["plot_shown"].is_set():
            print("    [Galileo:] WARNING: A plot window should had already been open. Command ignored.")
        else:
            self.plotStatus["command_done"].clear()
            print("    [Galileo:] Waiting for a plot window to open......")
            with self.pipeLock:
                self.mainConn.send(("replot",[]))
            self.plotStatus["plot_shown"].wait()
            time.sleep(self.UI_LAG)
            print("    [Galileo:] A plot window should have opened.\n")
        self.prompt()
            
    def autoscaleOn(self):
        self.plotStatus["command_done"].clear()
        print("    [Galileo:] Turning auto-scale on......")
        with self.pipeLock:
            self.mainConn.send(("autoscale_on",[]))
        self.plotStatus["command_done"].wait()
        time.sleep(self.UI_LAG)
        print("    [Galileo:] Auto-scale is on.\n")
        self.prompt()
        
    def autoscaleOff(self):    
        self.plotStatus["command_done"].clear()
        print("    [Galileo:] Turning auto-scale off......")
        with self.pipeLock:
            self.mainConn.send(("autoscale_off",[]))
        self.plotStatus["command_done"].wait()
        time.sleep(self.UI_LAG)
        print("    [Galileo:] Auto-scale is off.\n")
        self.prompt()
        
    def clearPlot(self):
        self.plotStatus["command_done"].clear()
        print("    [Galileo:] Clearing plotting buffer......")
        with self.pipeLock:
            self.mainConn.send(("clear",[]))
        self.plotStatus["command_done"].wait()
        time.sleep(self.UI_LAG)
        print("    [Galileo:] Done.\n")
        self.prompt()
    
    def wrongCommand(self, command):
        print("    [Galileo:] WARNING: Unrecognised command: \"{}\".\n".format(command))
        self.prompt()
    
    def prompt(self):
        print("{0}{1}".format(self.QUESTIONS[random.randrange(len(self.QUESTIONS))], self.PROMPT), end="")


        
    def start(self):
        # Start the plotting service
        print("    [Galileo:] Starting the live data plotting service......")
        
        # Initialize the plot status indicators and send through the pipe
        self.plotStatus = {"plot_shown": multiprocessing.Event(),
                           "command_done": multiprocessing.Event(),
                           "request_data": multiprocessing.Event()
                        }
        self.plotStatus["plot_shown"].clear()
        self.plotStatus["command_done"].clear()
        self.plotStatus["request_data"].clear()
        
        self.plotProc = multiprocessing.Process(target=self.plottingProc, name="Galileo: Data plotting",
                                           kwargs={"status": self.plotStatus,
                                                   "plotConn": self.plotConn,
                                                   "processLock": self.processLock,
                                                   "xyVars": self.plotXYs,
                                                   "xyLabels": self.plotLabels,
                                                   "refreshInterval": self.plot_refresh_interval,
                                                   "listenInterval": self.plot_listen_interval,
                                                   }
                                           )

        self.plotProc.start()
        
        # Wait for the plotting service to give its first data inquiring signal
        self.plotStatus["request_data"].wait()
        print("    [Galileo:] Live data plotting service has started.\n")
        
                # start the experiment
        print("""\
        starting the following experiment:
            +----------------------------------------+
            |{0:^40}|
            +----------------------------------------+\n""".format(self.experiment.title))
            
        self.experiment.start()
        
        self.measureThread = threading.Thread(target=self.keepMeasuring, name="Galileo: Measurements", args=(self.mainConn, self.processLock, self.pipeLock, self.dataLock))
        self.measureThread.start()
        
        print ("    [Galileo:] Measurements have started.\n\n    [Galileo:] Waiting for a plot window to open......")
        self.plotStatus["plot_shown"].wait() 
        self.prompt()