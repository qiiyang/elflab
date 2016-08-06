import csv

import numpy as np

import elflab.datasets as datasets

# Import a MPMS data file   
def loadfile(filename):
    # initialize lists for reading
    ltime = []
    lT = []
    lH = []
    lM = []
    lMerr = []
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
                    lT.append(float(row[2]))
                except ValueError:
                    lT.append(np.nan)
                    
                try:
                    lH.append(float(row[3]))
                except ValueError:
                    lH.append(np.nan)
                    
                try:
                    lM.append(float(row[4]))
                except ValueError:
                    lM.append(np.nan)
                    
                try:
                    lMerr.append(float(row[5]))
                except ValueError:
                    lMerr.append(np.nan)
                
    # Convert lists to datasets (dicts of 1D numpy arrays)
    data = datasets.DataSet([
                            ("time", np.array(ltime, dtype=np.float_, copy=True)),
                            ("T", np.array(lT, dtype=np.float_, copy=True)),
                            ("H", np.array(lH, dtype=np.float_, copy=True)),
                            ("M", np.array(lM, dtype=np.float_, copy=True)),
                            ("err_M", np.array(lMerr, dtype=np.float_, copy=True))
                            ])
    return data