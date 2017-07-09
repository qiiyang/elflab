##########################################
# General Purpose Signal Processing ######
##########################################
import math
import numpy as np

# modify a averager to decorrelate n neighbours 
def decorrelate_neighbour_averager(n, averager, estimate_error=False):
    # The new averager
    def new_averager(data):
        if estimate_error and (len(data) <= n):
            return float("nan")
        else:
            decorrelated = np.empty((len(data) - 1) // n + 1)
            for i in range(len(decorrelated)):
                decorrelated[i] = np.nanmedian(data[i * n : (i + 1) * n])
            return averager(decorrelated)
    # Standard error estimator
    # Assuming no irreducible error in the mean
    def new_se(data, _):
        if len(data) <= n:
            return float("nan")
        else:
            # First estimate the population standard deviation by periodic sampling
            m = 0
            sd = 0.0
            indices = np.arange(len(data))
            for i in range(n):
                sample = data[indices % n == i]
                if len(sample) >= 2:
                    m += 1
                    sd += np.std(sample, ddof=1)
            sd /= m
            # calculate the standard error by central limit theorem
            se = sd / math.sqrt((len(data) - 1) // n + 1)
            return se
    if estimate_error:
        return (new_averager, new_se)
    else:
        return (new_averager, None)