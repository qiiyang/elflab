# Correcting temporal drifts

import numpy as np

from elflab import constants, abstracts
import elflab.datasets as datasets

# Correcting a linear drift of a quantity vs time
def linear(data, key, t1, v1, t2, v2): # key is the name of the drifting quantity; (t, v) are two data points defining a linear temporal drifts
    # Define drifts as v_new = v - k(t-t0), where t0 = (t1+t2)/2
    t0 = (t1 + t2) / 2.0
    k = (v2 - v1) / (t2 - t1)
    shifted = data.duplicate()
    shifted[key] = data[key] - k * (shifted["time"] - t0)
    return shifted