import math
import csv

import numpy as np
import scipy.optimize

from elflab import constants, abstracts
import elflab.datasets as datasets

# For a pair of R's obtained by the van der Pauw method, compute the sheet resistance Rs, using the Brent1973 method
def van_der_Pauw(R_horizontal, R_vertical, xtol=1e-12, rtol=4.4408920985006262e-16, maxiter=100):
    # Defining the equation f(Rs)=0
    def f(Rs):
        A = math.exp(-consts.pi * R_horizontal / Rs)
        B = math.exp(-consts.pi * R_vertical / Rs)
        return A + B - 1.
    if R_horizontal < R_vertical:
        R1 = R_horizontal
        R2 = R_vertical
    else:
        R2 = R_horizontal
        R1 = R_vertical
    Rmin = consts.pi * R1 /consts.ln2 - xtol
    Rmax = consts.pi * (R1+R2) / 2. /consts.ln2 + xtol
    
    Rs = scipy.optimize.brentq(f, Rmin, Rmax, args=(), xtol=xtol, rtol=rtol, maxiter=maxiter, full_output=False, disp=True)
    return Rs
    
# Symmetrise / Antisymmetrise magnetoresistance data, by default using linear interpolation
def symmetrize_MR(data, mirror, spline_order=1):    # data and its mirror
    # Sort the mirror set by H
    sorted_mirror = mirror.sort("H")
    # prepare the interpolators
    mirror_R = mirror.interpolator("H", "R", order=spline_order)
    mirror_err_R = mirror.interpolator("H", "err_R", order=spline_order)
    
    # filtering through data, only getting data points where H is in range of the mirror
    indices = [i for i in range(len(data["H"]))
                    if (data["H"][i] <= -(sorted_mirror["H"][0])) and (data["H"][i] >= -(sorted_mirror["H"][-1]))]
    result = data.empty()
    for key in data:
        result[key] = data[key][indices]
        
    # compute symmetrized R and its standard error
    result["R"] = 0.5 * (result["R"] + mirror_R(-result["H"]))
    result["err_R"] = 0.5 * (result["err_R"]**2 + mirror_err_R(-result["H"])**2)**0.5
    
    return result