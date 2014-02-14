""" The main script to run the measurements with a mutual inductance probe
"""

# ____Computing Parameters
DEBUG_INFO = False

# Parameters to be set by the user for each measurement
# ____Plot Parameters
NROWS = 2   # number of rows of sub plots
NCOLS = 1   # number of columns of sub plots
XYVARS = [
            [("T", "X")],
            [("T", "Y")]
         ]      # Names of variable pairs to plot in each sub-plot

            
# Set search paths
import sys
import os
# _____Find LabPy root path and add to search path
labPyPath = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, labPyPath)
if DEBUG_INFO:
    print ("-------------------------\n##### Debug Info 1 #####\nsys.path =\n   {}\n-------------------------\n".format(sys.path))
    
# Import other modules
import numpy as np
import mi_common as mi

