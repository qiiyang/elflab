import math
import csv

import numpy as np
import scipy.optimize

from elflab import constants, abstracts
import elflab.datasets as datasets    
    
def median(data, var = None, interval):
# filter the data with a median filter, per (interval) in (var)
# if var == None, interval is the number of data point
    if var is None:
        return datasets.downsample(dataset, size, averaging=np.nanmedian , error_est=None)
    else:
        filtered_lists = {}
        for key in data:
            filtered_lists[key] = []
        sorted = data.sort(var)
        i1 = 0
        while i1 < sorted.length:
            i0 = i1
            v0 = sorted[var][i0]
            v1 = v0
            while (i1 < soorted.length) and (v1 - v0 < interval):
                i1 += 1
                v1 = sorted[var][i1]
            for key in sorted:
                med = np.nanmedian(sorted[key][v0:v1])
                filtered_listes[key].append(nan)