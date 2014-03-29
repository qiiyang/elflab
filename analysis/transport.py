import math
import csv

import numpy as np
import scipy.optimize
import elflab.constants as consts

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