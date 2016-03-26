""" Implementation of plotting live data from measurements, utilizing multi-processing
"""

# Global flags
DEBUG_INFO = False
SCIENTIFIC_NOTATION_POWER = 4  # Minimum power to use scientific notation

# import modules
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time
import threading
import multiprocessing

class PlotLive:
    """ Implementation of plotting live data from measurements"""
    
    # Computing-related constants
    MAXFLOATS = 10**7     # The maximum number of float numbers to be stored
    INITFLOATS = 1000    # Initial buffer size, as number of float stored
    DOWNSAMPLERATIO = 10    # Down-sampling ratio, when the buffer is full
    SMALL = 1.e-9       # a very small non-zero
    BLIT = True        # whether to blit
    
    # Graph-related constants
    LW = 2      # line width
    OVERRANGE = 0.05     # percentage to over-range the axes
    DEFAULT_PERIOD = 0.3   # in s
    MARKERPOOL = ["x", "+", "o", "s", "^", "D", "*"]     # pools of plotting markers
    COLOURPOOL = ["b", "g", "r", "k", "y", "m"]     # pools of colours
    
    # flags
    flag_quit = False       # True if user commanded quit
    flag_replot = True     # True if asked to replot
    flag_autoscale = True
    flag_newData = False    # True if there are new data to be updated to the plot
        
        
    # The constructor
    def __init__(self, status, plotConn, xyVars, xyLabels, refreshInterval=DEFAULT_PERIOD, listenInterval=DEFAULT_PERIOD):
                # self, (one end of a Pipe), process lock,, (list of variables to plot in each subplots), (list of labels), refresh interval in s, sampling interval in s
        
        # Save constants
        self.status = status
        self.plotConn = plotConn
        self.xyVars = xyVars
        self.xyLabels = xyLabels
        self.listenInterval = listenInterval
        self.refreshInterval = refreshInterval
        
        # Calculate derived constants
        self.nrows = nrows = len(xyVars)
        self.ncols = ncols = len(xyVars[0])
        self.maxPoints = self.MAXFLOATS // (nrows * ncols * 2)      # maximum number of datapoints
        self.bufPoints = self.INITFLOATS // (nrows * ncols * 2)     # initial buffer size
        self.styles = []     # plotting style strings for each sub-plot
        for i in range(nrows):
            self.styles.append([])
            for j in range(ncols):
                k = i*ncols + j
                self.styles[i].append(self.COLOURPOOL[k % len(self.COLOURPOOL)] + self.MARKERPOOL[k % len(self.MARKERPOOL)])
        if DEBUG_INFO:
            print("##### Debug Info: class PlotLive #####\n------------------------\n    styles ==\n{}\n------------------------".format(self.styles))
        
        # Initialise the axis number formatter:
        self.y_formatter = matplotlib.ticker.ScalarFormatter(useOffset=False)
        self.y_formatter.set_powerlimits((-SCIENTIFIC_NOTATION_POWER, SCIENTIFIC_NOTATION_POWER))
        
        # Initialise the plot buffer
        self.nPoints = 0
        self.xys = np.empty([nrows, ncols, 2, self.bufPoints], dtype=float, order='C')    # the buffer
        
        # Initialise the record of extrema of x's and y's for each sub plots
        self.xyLims = np.empty((nrows, ncols, 2, 2))
        self.xyLims[:,:,:,0].fill(float("inf"))
        self.xyLims[:,:,:,1].fill(float("-inf"))
        
        # Initialize listener threading
        self.dataLock = threading.RLock()
        self.listenThread = threading.Thread(target = self.listen, name = "Galileo: plot listener")

    # Communication with the parent process                    
    def listen(self):
        while not self.flag_quit:
            # Setting the request-data signal
            self.status["request_data"].set()
            
            # parsing the pipe flow
            while self.plotConn.poll() and not self.flag_quit:
                command, dataPoint = self.plotConn.recv()      # Command and value
                # Update flags
                with self.dataLock:
                    if command == "quit":
                        self.flag_quit = True
                        plt.close('all')
                        self.status["command_done"].set()
                    elif command == "replot":
                        self.flag_replot = True
                    elif command == "autoscale_on":
                        self.flag_autoscale = True
                        self.status["command_done"].set()
                    elif command == "autoscale_off":
                        self.flag_autoscale = False
                        self.status["command_done"].set()
                    elif command == "clear":
                        self.xys[:, :, :, 0:2] = self.xys[:, :, :, self.nPoints-2 : self.nPoints]
                        for i in range(self.nrows):
                            for j in range(self.ncols):
                                xMin = min(self.xys[i, j, 0, 0:2])
                                xMax = max(self.xys[i, j, 0, 0:2])
                                yMin = min(self.xys[i, j, 1, 0:2])
                                yMax = max(self.xys[i, j, 1, 0:2])
                                
                                self.xyLims[i, j, 0] = xMin, xMax
                                self.xyLims[i, j, 1] = yMin, yMax
                                
                        self.flag_newData = True
                        self.nPoints = 2
                        self.status["command_done"].set()
                    elif command == "data":
                        # Store data in buffer
                        self.nPoints += 1
                        # ____Check buffer size
                        if self.nPoints > self.maxPoints:
                            # Down-sampling old data
                            if DEBUG_INFO:
                                print("[DEBUG: LivePlot] Plotting buffer full, down-sampling.")
                            self.nPoints = self.maxPoints // self.DOWNSAMPLERATIO
                            for i in range(self.nPoints):
                                self.xys[:, :, :, i] = self.xys[:, :, :, i * self.DOWNSAMPLERATIO]
                        elif self.nPoints > self.bufPoints:
                            # Extend the buffer
                            newLen = self.bufPoints * 2     # The new buffer length
                            if newLen > self.maxPoints:
                                newLen = self.maxPoints
                            ext = np.empty((self.nrows, self.ncols, 2, newLen - self.bufPoints))
                            self.xys = np.append(self.xys, ext, axis=3)
                            if DEBUG_INFO:
                                print ("Extended plotting buffer, {0} -> {1}".format(self.bufPoints, newLen))
                            self.bufPoints = newLen
                        # ____Store data
                        k = self.nPoints - 1
                        for i in range(self.nrows):
                            for j in range(self.ncols):
                                self.xys[i, j, 0, k] = x = dataPoint[i][j][0]
                                self.xys[i, j, 1, k] = y = dataPoint[i][j][1]
                                # Recalculating min's & max's
                                xMin, xMax = self.xyLims[i, j, 0] 
                                yMin, yMax = self.xyLims[i, j, 1] 
                                
                                xMin = min(x, xMin)
                                xMax = max(x, xMax)
                                yMin = min(y, yMin)
                                yMax = max(y, yMax)
                                
                                self.xyLims[i, j, 0] = xMin, xMax
                                self.xyLims[i, j, 1] = yMin, yMax
                        self.flag_newData = True
                    else:
                        print("[WARNING: plot_live] Unrecognised command: {}\n".format(command))
            # Wait
            if not self.flag_quit:
                time.sleep(self.listenInterval)
    
    # Generator for animation
    def genCheckFlags(self):
        while not self.flag_quit:
            yield True
                
    # Function to update the plots
    def update(self, updating):
                    # dataPoint[i][j] = (x, y) for sub-plot(i,j)
        with self.dataLock:
            if self.flag_newData:
                self.flag_newData = False
                k = self.nPoints - 1
                flag_rescale = False

                for i in range(self.nrows):
                    for j in range(self.ncols):
                        # Check wherther need to rescale
                        if (not flag_rescale) and self.flag_autoscale:
                            xMin, xMax = self.xyLims[i, j, 0] 
                            yMin, yMax = self.xyLims[i, j, 1]  
                            # Test whether x, y are out of range
                            # ____Get the scales of each axis
                            xScale = self.subs[i][j].get_xlim()
                            yScale = self.subs[i][j].get_ylim()
                            if (xMin < xScale[0]) or (xMax > xScale[1]) or (yMin < yScale[0]) or (yMax > yScale[1]):
                                flag_rescale = True

                        # Update the subplot    
                        self.lines[i*self.ncols+j].set_data(self.xys[i, j, 0, :k+1], self.xys[i, j, 1, :k+1])
                        
                # Rescale if necessary
                if flag_rescale:
                    self.rescale()
                    if self.BLIT:
                        self.fig.canvas.draw()
                    if DEBUG_INFO:
                        print ("rescalling")
        return self.lines
    
    # Function to rescale the plot
    def rescale(self):
        for i in range(self.nrows):
            for j in range(self.ncols):
                xMin, xMax = self.xyLims[i, j, 0]
                yMin, yMax = self.xyLims[i, j, 1]   
                
                delX = self.OVERRANGE * (xMax - xMin + self.SMALL)
                delY = self.OVERRANGE * (yMax - yMin + self.SMALL)
                
                self.subs[i][j].set_xlim (xMin - delX, xMax + delX)
                self.subs[i][j].set_ylim (yMin - delY, yMax + delY)     
    
    # Re-initialize the plot
    def replot(self):
        self.fig, self.subs= plt.subplots(self.nrows, self.ncols, squeeze=False)
        self.lines = []      # 1D list of Line2D objects
        # ____Plot sub-plots with current data, set the plot styles and save the Line2D objects
        for i in range(self.nrows):
            for j in range(self.ncols):
                line, = self.subs[i][j].plot(self.xys[i, j, 0, :self.nPoints], self.xys[i, j, 1, :self.nPoints], self.styles[i][j], lw=self.LW, label=self.xyVars[i][j][1])
                self.subs[i][j].set_xlabel(self.xyLabels[i][j][0])
                self.subs[i][j].set_ylabel(self.xyLabels[i][j][1])
                self.subs[i][j].grid()
                self.subs[i][j].legend()
                self.subs[i][j].yaxis.set_major_formatter(self.y_formatter)
                self.lines.append(line)
        if self.nPoints >= 2:
            self.rescale()

    # Initialisor for animation
    def initLines(self):
        with self.dataLock:
            for i in range(self.nrows):
                for j in range(self.ncols):
                    # Update the subplot    
                    self.lines[i*self.ncols+j].set_data([], [])
            self.flag_newData = True
        return self.lines
        
    
    # Function to animate the plot
    def start(self):
        self.listenThread.start()
        while not self.flag_quit:
            if self.flag_replot:
                while self.nPoints < 2:
                    time.sleep(self.refreshInterval)
                with self.dataLock:
                    self.replot()
                    self.flag_replot = False
                self.ani = animation.FuncAnimation(self.fig, func=self.update, frames=self.genCheckFlags, init_func=self.initLines, blit=self.BLIT, interval=self.refreshInterval*1000., repeat=False)
                self.status["plot_shown"].set()
                plt.show()
                self.status["plot_shown"].clear()
        self.listenThread.join()
        