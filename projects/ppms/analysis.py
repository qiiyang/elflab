import csv, math

import numpy as np

import elflab.datasets as datasets
 
# Import PPMS dc data    
def import_dc(filename):
    # initialize lists for reading
    ltime = []
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
        for row in reader:
            if row[0] == "":    # a valid data line only if the comment entry is ""
                try:
                    ltime.append(float(row[1]))
                except ValueError:
                    ltime.append(np.nan)
                    
                try:
                    lT.append(float(row[3]))
                except ValueError:
                    lT.append(np.nan)
                    
                try:
                    lH.append(float(row[4]))
                except ValueError:
                    lH.append(np.nan)
                    
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
                    lch1err.append(float(row[14]) / float(row[6]) * float(row[19]))
                except ValueError:
                    lch1err.append(np.nan)
                
                try:
                    lch2err.append(float(row[15]) / float(row[8]) * float(row[20]))
                except ValueError:
                    lch2err.append(np.nan)
                    
                try:
                    lch3err.append(float(row[16]) / float(row[10]) * float(row[21]))
                except ValueError:
                    lch3err.append(np.nan)
                
    # Convert lists to datasets (dicts of 1D numpy arrays)
    ch1 = datasets.DataSet([
                            ("time", np.array(ltime, dtype=np.float_, copy=True)),
                            ("T", np.array(lT, dtype=np.float_, copy=True)),
                            ("H", np.array(lH, dtype=np.float_, copy=True)),
                            ("R", np.array(lch1R, dtype=np.float_, copy=True)),
                            ("err_R", np.array(lch1err, dtype=np.float_, copy=True))
                            ])
    ch2 = datasets.DataSet([
                            ("time", np.array(ltime, dtype=np.float_, copy=True)),
                            ("T", np.array(lT, dtype=np.float_, copy=True)),
                            ("H", np.array(lH, dtype=np.float_, copy=True)),
                            ("R", np.array(lch2R, dtype=np.float_, copy=True)),
                            ("err_R", np.array(lch2err, dtype=np.float_, copy=True))
                            ])
    ch3 = datasets.DataSet([
                            ("time", np.array(ltime, dtype=np.float_, copy=True)),
                            ("T", np.array(lT, dtype=np.float_, copy=True)),
                            ("H", np.array(lH, dtype=np.float_, copy=True)),
                            ("R", np.array(lch3R, dtype=np.float_, copy=True)),
                            ("err_R", np.array(lch3err, dtype=np.float_, copy=True))
                            ])
    return (ch1, ch2, ch3)