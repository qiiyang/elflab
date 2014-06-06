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
        A = math.exp(-constants.pi * R_horizontal / Rs)
        B = math.exp(-constants.pi * R_vertical / Rs)
        return A + B - 1.
    if R_horizontal < R_vertical:
        R1 = R_horizontal
        R2 = R_vertical
    else:
        R2 = R_horizontal
        R1 = R_vertical
    Rmin = constants.pi * R1 /constants.ln2 - xtol
    Rmax = constants.pi * (R1+R2) / 2. /constants.ln2 + xtol
    
    Rs = scipy.optimize.brentq(f, Rmin, Rmax, args=(), xtol=xtol, rtol=rtol, maxiter=maxiter, full_output=False, disp=True)
    return Rs

# For a pair of data sets, calculating the sets of sheet resistance by van der Pauw method, using "param" as the interpolation parameter
def van_der_Pauw_set(set1, set2, param):
    # sort set2 according to param
    set2sorted = set2.sort(param)
    # filter set1 to have param within the range of set2
    indices = [i for i in range(len(set1[param]))
                    if (set1[param][i] >= set2sorted[param][0]) and (set1[param][i] <= set2sorted[param][-1])]
    result = set1.empty()
    for key in result:
        result[key] = set1[key][indices]
    # Compute VdP sheet resistance
    set2R = set2sorted.interpolator(param, "R")
    set2err = set2sorted.interpolator(param, "err_R")
    for i in range(len(result[param])):
        x = result[param][i]
        R1 = result["R"][i]
        dR1 = result["err_R"][i]
        R2 = set2R(x)
        dR2 = set2err(x)
        Rs = van_der_Pauw(R1, R2)
        result["R"][i] = Rs
        result["err_R"][i] = dR1 + dR2  # Very approximately
    return result

# Split MR into down and up sweeps
def split_MR_down_up(data):
    # Find the minimum
    minimum = 9.e20
    index = 0
    for i in range(len(data["H"])):
        if data["H"][i] < minimum:
            index = i
            minimum = data["H"][i]
    up = data.empty()
    down = data.empty()
    for key in data:
        down[key] = data[key][:index].copy()
        up[key] = data[key][index:].copy()
    return (down, up)    
    

    
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
    
def antisymmetrize_MR(data, mirror, spline_order=1):    # data and its mirror
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
    result["R"] = 0.5 * (result["R"] - mirror_R(-result["H"]))
    result["err_R"] = 0.5 * (result["err_R"]**2 + mirror_err_R(-result["H"])**2)**0.5
    
    return result