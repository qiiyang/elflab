""" The main script to run the measurements with a mutual inductance probe

"""

# Parameters to be set by the user for each measurement
# ____Plot Parameters
NROWS = 2   # number of rows of sub plots
NCOLS = 1   # number of columns of sub plots
LW = 2      # default line width

# ____Computing Parameters
debug_info = False
MAXPOINTS = 1000000     # The maximum number of data points
SMALL = 1.e-10      # smallest non-zero

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
plotBuffer = mi.initialData.copy()# The buffer for data-plotting


buffer_ready = True     # Flag for data-plotting

# ____Initialise plots
xys = np.empty([NROWS, NCOLS, 2, MAXPOINTS], dtype=float)
xys.fill(float("nan"))

fig, subs = plt.subplots(NROWS, NCOLS, squeeze=False)

lines = []
for i in range(NROWS):
    linerow = []
    for j in range(NCOLS):
        line, = subs[i][j].plot([], [], markers[i][j], lw=LW)
        subs[i][j].set_xlim(1., -1.)
        subs[i][j].set_ylim(1., -1.)
        subs[i][j].grid()
        linerow.append(line)
    lines.append(linerow)
    
# Function to update the plot
k = 0
def updatePlot(n):
    global k
    redraw = False
    plotBuffer["n"] += 1
    for i in range(NROWS):
        for j in range(NCOLS):
            xys[i, j, 0, k] = x = plotBuffer[xNames[i][j]]
            xys[i, j, 1, k] = y = plotBuffer[yNames[i][j]]
            xMin, xMax = subs[i][j].get_xlim()   
            yMin, yMax = subs[i][j].get_ylim()
            
            if redraw or (x < xMin) or (x > xMax) or (y < yMin) or (y > yMax):
                redraw = True
                xMin = min(x, xMin)
                xMax = max(x, xMax)
                yMin = min(y, yMin)
                yMax = max(y, yMax)
                subs[i][j].set_xlim (xMin - 0.01 * (xMax - xMin) - SMALL, xMax + 0.01 * (xMax - xMin) + SMALL)
                subs[i][j].set_ylim (yMin - 0.01 * (yMax - yMin) - SMALL, yMax + 0.01 * (yMax - yMin) + SMALL)
            lines[i][j].set_data(xys[i, j, 0], xys[i, j, 1])
    k += 1
    if redraw:
        fig.canvas.draw()
        
    return lines[0][0],

# Animate!
ani = animation.FuncAnimation(fig, updatePlot, frames=60, blit=False, interval=10, repeat=False)
plt.show()