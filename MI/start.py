""" The main script to run the measurements with a mutual inductance probe

"""

# Parameters to be set by the user for each measurement
debug_info = True

NROWS = 2   # number of rows of sub plots
NCOLS = 1   # number of columns of sub plots
LW = 2      # default line width

# ____Data to use as x-axis for each sub-plots
xNames = [["n"],
        ["n"]]

# ____data to be plotted as y axis in each sub-plots
yNames = [["X"],
           ["Y"]]
           
# ____ plotting markers per sub-plots
markers = [["bx"],
            ["r+"]]

            
# Set search paths
import sys
import os
# _____Find LabPy root path and add to search path
labPyPath = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, labPyPath)
if debug_info:
    print ("-------------------------\n##### Debug Info 1 #####\nsys.path =\n   {}\n-------------------------\n".format(sys.path))
    
# Import other modules
import numpy as np
import mi_common as mi
import matplotlib.pyplot as plt
import matplotlib.animation as animation

if debug_info:
    print ("-------------------------\n##### Debug Info 2 #####\nImport Finished\n-------------------------\n")

# Global Variables
# ____Initialise the plotting buffer
plotBuffer = {  "n": 0.,     # data point index
                "t": 1.,     # time stamp in s
                "T": 2.,     # temperature in K
                "H": 3.,     # magnetic field in T
                "X": 4.,     # lock-in X in V
                "Y": 5.,     # lock-in Y in V
                "I_therm": 6.,   # thermometer current
                "V_therm": 7.   # thermometer voltage
                }   # The buffer for data-plotting


buffer_ready = True     # Flag for data-plotting

# ____Initialise plots
fig, subs = plt.subplots(NROWS, NCOLS, squeeze=False)
plt.autoscale(True, 'both', True)
lines = []
for i in range(NROWS):
    linerow = []
    for j in range(NCOLS):
        line, = subs[i][j].plot([1], [1], markers[i][j], lw=LW)
        linerow.append(line)
    lines.append(linerow)

# Function to update the plot
def updatePlot(n):
    plotBuffer["n"] += 1
    for i in range(NROWS):
        for j in range(NCOLS):
            x = plotBuffer[xNames[i][j]]
            y = plotBuffer[yNames[i][j]]
            linedata = lines[i][j].get_xydata()
            #print(np.array([[x, y]]))
            point = np.array([[x, y]])
            linedata = np.concatenate((linedata, point), axis=0)
            lines[i][j].set_data(linedata)
    return lines[0][0],

# Animate!
ani = animation.FuncAnimation(fig, updatePlot, frames=60, blit=True, interval=1, repeat=False)
plt.show()