""" Implementation of plotting live data from measurements, utilizing multi-processing
"""

# Global flags
DEBUG_INFO = False

# import modules
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time
import threading

class PlotLive:
    """ Implementation of plotting live data from measurements"""
    
    # Computing-related constants
    MAXFLOATS = 100000000     # The maximum number of float numbers to be stored
    INITFLOATS = 10000    # Initial buffer size, as number of float stored
    SMALL = 1.e-9       # a very small non-zero
    BLIT = False        # whether to blit
    
    # Graph-related constants
    LW = 2      # line width
    OVERRANGE = 0.05     # percentage to over-range the axes
    DEFAULT_PERIOD = 0.3   # in s
    MARKERPOOL = ["x", "+", "o", "s", "^", "D", "*"]     # pools of plotting markers
    COLOURPOOL = ["b", "g", "r", "k", "y", "m"]     # pools of colours
    
    # flags
    flag_stop = False   # True if Measurements stopped
    flag_quit = False       # True if user commanded quit
    flag_replot = True     # True if asked to replot
    flag_alive = False      # True if there's an open plot window
    flag_autoscale = True
        
        
    # The constructor
    def __init__(self, processLock, pipeEnd, nrows=1, ncols=1, xyVars=[[("", "")]], xyLabels=[[("", "")]], listenPeriod=DEFAULT_PERIOD, refreshPeriod=DEFAULT_PERIOD):
                # self, (one end of a Pipe), (No. of rows of subplots), (No. of cols), (list of variables to plot in each subplots), (list of labels), sampling interval in s, refresh interval in s
        
        # Save constants
        self.processLock = processLock
        self.pipeEnd = pipeEnd
        self.nrows = nrows
        self.ncols = ncols
        self.xyVars = xyVars
        self.xyLabels = xyLabels
        self.listenPeriod = listenPeriod
        self.refreshPeriod = refreshPeriod
        
        # Calculate derived constants
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
        
        # Initialise the plot buffer
        self.nPoints = 0
        self.xys = np.empty([nrows, ncols, 2, self.bufPoints], dtype=float, order='C')    # the buffer
        
        # Initialise the record of extrema of x's and y's for each sub plots
        self.xyLims = np.empty((nrows, ncols, 2, 2))
        self.xyLims[:,:,:,0].fill(float("inf"))
        self.xyLims[:,:,:,1].fill(float("-inf"))
                
        # Initialize listener threading
        self.threadLock = threading.RLock()
        self.listenThread = threading.Thread(target = self.listen, name = "Galileo: plot listener")

    # Communication with the parent process                    
    def listen(self):
        while not self.flag_quit:
            # Inquire data from the pipe
            self.pipeEnd.send(self.flag_alive)     # True if plot window exits
            while not self.pipeEnd.poll():
                time.sleep(self.listenPeriod / 10.)
                
            while self.pipeEnd.poll() and not self.flag_quit:
                command, dataPoint = self.pipeEnd.recv()      # Command and value
                # Update flags
                with self.threadLock:
                    if command == "quit":
                        self.flag_quit = True
                        plt.close()
                    elif command == "stop":
                        self.flag_stop = True
                    elif command == "autoscale on":
                        self.flag_autoscale = True
                    elif command == "autoscale off":
                        self.flag_autoscale = False
                    elif command == "replot":
                        self.flag_replot = True
                    elif command == "data":
                        # Store data in buffer
                        k = self.nPoints
                        self.nPoints += 1
                        # ____Check buffer size
                        if self.nPoints > self.maxPoints:
                            print("Plotting buffer is full!")
                            self.flag_stop = True
                            break
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
            # Wait
            time.sleep(self.listenPeriod)
    
    # Generator for animation
    def genCheckFlags(self):
        while not (self.flag_stop or self.flag_quit):
            yield True
                
    # Function to update the plots
    def update(self, updating):
                    # dataPoint[i][j] = (x, y) for sub-plot(i,j)
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
                self.lines.append(line)
        if self.nPoints >= 2:
            self.rescale()

        
    
    # Function to animate the plot
    def start(self):
        self.listenThread.start()
        while not self.flag_quit:
            if self.flag_replot:
                while self.nPoints < 2:
                    time.sleep(self.refreshPeriod)
                with self.threadLock:
                    self.replot()
                    self.flag_replot = False
                    self.flag_alive = True
                self.ani = animation.FuncAnimation(self.fig, self.update, self.genCheckFlags, blit=self.BLIT, interval=self.refreshPeriod*1000., repeat=False)
                plt.show()
                self.flag_alive = False
                time.sleep(self.refreshPeriod)
            
        self.listenThread.join()