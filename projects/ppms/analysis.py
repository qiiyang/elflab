import csv

import numpy as np
import scipy.interpolate as interpolate

class PpmsData:
    # Data format T, H, ch1R, ch1err, ch2R, ch2err, ch3R, ch3err
    T = None
    H = None
    ch1R = None
    ch2R = None
    ch3R = None
    ch1err = None
    ch2err = None
    ch3err = None
    
# Import PPMS dc data    
def import_dc(filename):
    # initialize lists for reading
    lT = []
    lH = []
    lch1R = []
    lch1err = []
    lch2R = []
    lch2err = []
    lch3R = []
    lch3err = []
    # reading data
    with open(filename, "r", newline='') as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:   
            lT.append(row[3])
            lH.append(row[4])
            lch1R.append(row[19])
            lch2R.append(row[20])
            lch3R.append(row[21])
            lch1err.append(row[14])
            lch2err.append(row[15])
            lch3err.append(row[16])
    data = PpmsData()
    data.T = np.array(lT, dtype=np.float_)
    data.H = np.array(lH, dtype=np.float_)
    data.ch1R = np.array(lch1R, dtype=np.float_)
    data.ch2R = np.array(lch2R, dtype=np.float_)
    data.ch3R = np.array(lch3R, dtype=np.float_)
    data.ch1err = np.array(lch1err, dtype=np.float_) * 1.e3
    data.ch2err = np.array(lch1err, dtype=np.float_) * 1.e3
    data.ch3err = np.array(lch1err, dtype=np.float_) * 1.e3
    return data

# Symmetrise / Antisymmetrise dc MR data   
def symmetrise_dc(data1, data2):
    sym1 = PpmsData()
    sym1.T = data1.T.copy()
    sym1.H = data1.H.copy()
    sym1.ch1err = data1.ch1err.copy()
    sym1.ch2err = data1.ch2err.copy()
    sym1.ch3err = data1.ch3err.copy()
    
    sym2 = PpmsData()
    sym2.T = data2.T.copy()
    sym2.H = data2.H.copy()
    sym2.ch1err = data2.ch1err.copy()
    sym2.ch2err = data2.ch2err.copy()
    sym2.ch3err = data2.ch3err.copy()
    
    # interpolate with linear spline
    interpolator = interpolate.UnivariateSpline(data2.H, data2.ch1R, k=1, s=0)
    sym1.ch1R = 0.5 * (data1.ch1R + interpolator(-sym1.H))
    
    interpolator = interpolate.UnivariateSpline(data2.H, data2.ch2R, k=1, s=0)
    sym1.ch2R = 0.5 * (data1.ch2R + interpolator(-sym1.H))
    
    interpolator = interpolate.UnivariateSpline(data2.H, data2.ch3R, k=1, s=0)
    sym1.ch3R = 0.5 * (data1.ch3R + interpolator(-sym1.H))
    
    interpolator = interpolate.UnivariateSpline(data1.H, data1.ch1R, k=1, s=0)
    sym2.ch1R = 0.5 * (data2.ch1R + interpolator(-sym2.H))
    
    interpolator = interpolate.UnivariateSpline(data1.H, data1.ch2R, k=1, s=0)
    sym2.ch2R = 0.5 * (data2.ch2R + interpolator(-sym2.H))
    
    interpolator = interpolate.UnivariateSpline(data1.H, data1.ch3R, k=1, s=0)
    sym2.ch3R = 0.5 * (data2.ch3R + interpolator(-sym2.H))
    
    return (sym1, sym2)
    
def antisymmetrise_dc(data1, data2):
    sym1 = PpmsData()
    sym1.T = data1.T.copy()
    sym1.H = data1.H.copy()
    sym1.ch1err = data1.ch1err.copy()
    sym1.ch2err = data1.ch2err.copy()
    sym1.ch3err = data1.ch3err.copy()
    
    sym2 = PpmsData()
    sym2.T = data2.T.copy()
    sym2.H = data2.H.copy()
    sym2.ch1err = data2.ch1err.copy()
    sym2.ch2err = data2.ch2err.copy()
    sym2.ch3err = data2.ch3err.copy()
    
    # interpolate with linear spline
    interpolator = interpolate.UnivariateSpline(data2.H, data2.ch1R, k=1, s=0)
    sym1.ch1R = 0.5 * (data1.ch1R - interpolator(-sym1.H))
    
    interpolator = interpolate.UnivariateSpline(data2.H, data2.ch2R, k=1, s=0)
    sym1.ch2R = 0.5 * (data1.ch2R - interpolator(-sym1.H))
    
    interpolator = interpolate.UnivariateSpline(data2.H, data2.ch3R, k=1, s=0)
    sym1.ch3R = 0.5 * (data1.ch3R - interpolator(-sym1.H))
    
    interpolator = interpolate.UnivariateSpline(data1.H, data1.ch1R, k=1, s=0)
    sym2.ch1R = 0.5 * (data2.ch1R - interpolator(-sym2.H))
    
    interpolator = interpolate.UnivariateSpline(data1.H, data1.ch2R, k=1, s=0)
    sym2.ch2R = 0.5 * (data2.ch2R - interpolator(-sym2.H))
    
    interpolator = interpolate.UnivariateSpline(data1.H, data1.ch3R, k=1, s=0)
    sym2.ch3R = 0.5 * (data2.ch3R - interpolator(-sym2.H))
    
    
    return (sym1, sym2)