import csv

import numpy as np

import elflab.datasets as datasets
 
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
            try:
                lch1R.append(float(row[19]))
            except ValueError:
                lch1R.append(np.nan)
                
            try:
                lch2R.append(float(row[20]))
            except ValueError:
                lch2R.append(np.nan)
            
            try:
                lch3R.append(float(row[21]))
            except ValueError:
                lch3R.append(np.nan)
            
            # Calculating the standard errors assuming the stupid default resistivity calculation made by PPMS
            try:
                lch1err.append(float(row[14]) * 1.e3 / float(row[18])**0.5)
            except ValueError:
                lch1err.append(np.nan)
            
            try:
                lch2err.append(float(row[15]) * 1.e3 / float(row[18])**0.5)
            except ValueError:
                lch2err.append(np.nan)
                
            try:
                lch3err.append(float(row[16]) * 1.e3 / float(row[18])**0.5)
            except ValueError:
                lch3err.append(np.nan)
                
    # Convert lists to datasets (dicts of 1D numpy arrays)
    ch1 = datasets.DataSet([
                            ("T", np.array(lT, dtype=np.float_, copy=True)),
                            ("H", np.array(lH, dtype=np.float_, copy=True)),
                            ("R", np.array(lch1R, dtype=np.float_, copy=True)),
                            ("err_R", np.array(lch1err, dtype=np.float_, copy=True))
                            ])
    ch2 = datasets.DataSet([
                            ("T", np.array(lT, dtype=np.float_, copy=True)),
                            ("H", np.array(lH, dtype=np.float_, copy=True)),
                            ("R", np.array(lch2R, dtype=np.float_, copy=True)),
                            ("err_R", np.array(lch2err, dtype=np.float_, copy=True))
                            ])
    ch3 = datasets.DataSet([
                            ("T", np.array(lT, dtype=np.float_, copy=True)),
                            ("H", np.array(lH, dtype=np.float_, copy=True)),
                            ("R", np.array(lch3R, dtype=np.float_, copy=True)),
                            ("err_R", np.array(lch3err, dtype=np.float_, copy=True))
                            ])
    return (ch1, ch2, ch3)