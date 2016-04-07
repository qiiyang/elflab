""" plotting static data from file
"""

import numpy as np
import matplotlib
import matplotlib.pyplot as plt

SCIENTIFIC_NOTATION_POWER = 4  # Minimum power to use scientific notation

class plot_static:
    # Graph-related constants
    LW = 2      # line width
    MARKERPOOL = ["x", "+", "o", "s", "^", "D", "*"]     # pools of plotting markers
    COLOURPOOL = ["b", "g", "r", "k", "y", "m"]     # pools of colours
    
    def __init__(self, xyVars, xyLabels):
        # self, (list of variables to plot in each subplots), (list of labels)
        
        # Save constants
        self.xyVars = xyVars
        self.xyLabels = xyLabels
        
        # Calculate derived constants
        self.nrows = nrows = len(xyVars)
        self.ncols = ncols = len(xyVars[0])
        self.styles = []     # plotting style strings for each sub-plot
        for i in range(nrows):
            self.styles.append([])
            for j in range(ncols):
                k = i*ncols + j
                self.styles[i].append(self.COLOURPOOL[k % len(self.COLOURPOOL)] + self.MARKERPOOL[k % len(self.MARKERPOOL)])
        # Initialise the axis number formatter:
        self.y_formatter = matplotlib.ticker.ScalarFormatter(useOffset=False)
        self.y_formatter.set_powerlimits((-SCIENTIFIC_NOTATION_POWER, SCIENTIFIC_NOTATION_POWER))
        
    def plot(self, data): # data as a dict of numpy arrays.
        self.fig, self.subs= plt.subplots(self.nrows, self.ncols, squeeze=False)
        # ____Plot sub-plots with data, set the plot styles and save the Line2D objects
        for i in range(self.nrows):
            for j in range(self.ncols):
                line, = self.subs[i][j].plot(data[self.xyVars[i][j][0]], data[self.xyVars[i][j][1]], self.styles[i][j], lw=self.LW, label=self.xyVars[i][j][1])
                self.subs[i][j].set_xlabel(self.xyLabels[i][j][0])
                self.subs[i][j].set_ylabel(self.xyLabels[i][j][1])
                self.subs[i][j].yaxis.set_major_formatter(self.y_formatter)
                self.subs[i][j].grid()
                self.subs[i][j].legend()
        plt.show()