""" plotting static data from file
"""

import numpy as np
import matplotlib
import matplotlib.pyplot as plt

class plot_static:
    # Graph-related constants
    MARKERPOOL = ["x", "+", "o", "s", "^", "D", "*"]     # pools of plotting markers
    COLOURPOOL = ["b", "g", "r", "k", "y", "m"]     # pools of colours
    
    def __init__(self, xyVars, xyLabels):
        # self, (list of variables to plot in each subplots), (list of labels)
        
        # Save constants
        self.status = status
        self.processLock = processLock
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