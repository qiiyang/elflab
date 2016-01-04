import math
import csv

import numpy as np
import scipy.optimize

from elflab import constants, abstracts
import elflab.datasets as datasets    
    
def median(data, var = None, interval):
# filter the data with a median filter, per (interval) in (var)
# if var == None, interval is the number of data point
    
    