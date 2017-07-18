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
    if math.isnan(R_horizontal) or math.isnan(R_vertical):
        Rs = float("nan")
    else:
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
    
# Van der Pauw error propagation
def van_der_Pauw_error(Rs, R1, R2, err_R1, err_R2):
    e1 = math.exp(-constants.pi * R1 / Rs)
    e2 = math.exp(-constants.pi * R2 / Rs)
    denorm = e1 * R1 / Rs + e2 * R2 / Rs
    # error squared
    err = math.sqrt((e1 / denorm * err_R1)**2 + (e2 / denorm * err_R2)**2)

# For a pair of data sets, calculating the sets of sheet resistance by van der Pauw method, using "param" as the interpolation parameter
def van_der_Pauw_set(set1, set2, param):
    # sort set2 according to param
    set2sorted = set2.sort(param)
    
    # filter set1 to have param within the range of set2
    indices = np.logical_and(set1[param] >= set2sorted[param][0], set1[param] <= set2sorted[param][-1])
    result = set1.mask(indices).duplicate()
    
    # Compute VdP sheet resistance
    set2R = set2sorted.interpolator(param, "R")
    set2err2 = set2sorted.error2_interpolator(param, "R")   # error squared
    for i in range(len(result[param])):
        R1 = result["R"][i]
        dR1 = result.errors["R"][i]
        
        x = result[param][i]
        R2 = set2R(x)
        dR2 = math.sqrt(set2err2(x))
        
        Rs = van_der_Pauw(R1, R2)
        result["R"][i] = Rs
        result.errors["R"][i] = van_der_Pauw_error(Rs, R1, R2, dR1, dR2)
    result.update()
    return result

# Split MR into down and up sweeps
def split_MR_down_up(data):
    # Find the minimum    
    index = np.argmin(data["H"])
    up = data.empty()
    down = data.empty()
    for key in data:
        down[key] = data[key][:index].copy()
        down.errors[key] = data.errors[key][:index].copy()
        up[key] = data[key][index:].copy()
        up.errors[key] = data.errors[key][index:].copy()
    up.update()
    down.update()
    return (down, up)   

    
# Symmetrise / Antisymmetrise magnetoresistance data, by default using linear interpolation
def symmetrize_MR(data, mirror, spline_order=1):    # data and its mirror
    has_errors = (data.errors is not None) and (mirror.errors is not None)
    # Sort the mirror set by H
    sorted_mirror = mirror.sort("H")
    # prepare the interpolators
    mirror_R = mirror.interpolator("H", "R", order=spline_order)
    if has_errors:
        mirror_err2 = mirror.error2_interpolator("H", "R", order=spline_order)
    
    # filtering through data, only getting data points where H is in range of the mirror
    indices = [i for i in range(len(data["H"]))
                    if (data["H"][i] <= -(sorted_mirror["H"][0])) and (data["H"][i] >= -(sorted_mirror["H"][-1]))]
    result = data.empty()
    for key in data:
        result[key] = data[key][indices].copy()
        result.errors[key] = data.errors[key][indices].copy()
    # compute symmetrized R and its standard error
    result["R"] = 0.5 * (result["R"] + mirror_R(-result["H"]))
    if has_errors:
        result.errors["R"] = 0.5 * np.sqrt(np.square(result.errors["R"]) + mirror_err2(-result["H"]))
    result.update()
    return result
    
def antisymmetrize_MR(data, mirror, spline_order=1):    # data and its mirror
    has_errors = (data.errors is not None) and (mirror.errors is not None)
    # Sort the mirror set by H
    sorted_mirror = mirror.sort("H")
    # prepare the interpolators
    mirror_R = mirror.interpolator("H", "R", order=spline_order)
    if has_errors:
        mirror_err2 = mirror.error2_interpolator("H", "R", order=spline_order)
    
    # filtering through data, only getting data points where H is in range of the mirror
    indices = [i for i in range(len(data["H"]))
                    if (data["H"][i] <= -(sorted_mirror["H"][0])) and (data["H"][i] >= -(sorted_mirror["H"][-1]))]
    result = data.empty()
    for key in data:
        result[key] = data[key][indices].copy()
        result.errors[key] = data.errors[key][indices].copy()
    # compute symmetrized R and its standard error
    result["R"] = 0.5 * (result["R"] - mirror_R(-result["H"]))
    if has_errors:
        result.errors["R"] = 0.5 * np.sqrt(np.square(result.errors["R"]) + mirror_err2(-result["H"]))
    result.update()
    return result
