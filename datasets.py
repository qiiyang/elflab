import csv

import numpy as np

import elflab.abstracts as abstracts
import scipy.interpolate as interpolate

class DataSet(abstracts.DataSetBase):
    def __init__(self, *args, **kwargs):
        super(DataSet, self).__init__(*args, **kwargs)
        self.sorted_views = {}
        
    # Create an empty dataset with identical variables
    def empty(self):
        new_set = DataSet()
        if self.errors is not None: # only true if the dataset has error values set
            new_set.errors = {}
        for key in self:
            new_set[key] = None
            if self.error is not None:
                new_set.error[key] = None
        return new_set
        
    # Define how exactly a dataset is to be copied, while not over-writing the copy() method
    def duplicate(self):
        new_set = DataSet()
        for key in self:
            new_set[key] = self[key].copy()
        if self.errors is not None:
            newset.errors = {}
            for key in self:
                new_set.errors[key] = self.errors[key].copy()
        return new_set
        
    # return a sorted copy
    def sort(self, key):
        # compute sorted indices
        if key in self.sorted_views:
            sorted = self.sorted_views[key]
        else:
            indices = np.argsort(self[key], kind='quicksort')
            sorted = DataSet()
            for k in self:
                sorted[k] = self[k][indices]
            if self.errors is not None:
                sorted.errors = {}
                for k in self:
                    sorted.errors[k] = self.errors[k][indices]
            self.sorted_views[key] = sorted
            sorted.sorted_views = self.sorted_views
        return sorted
        
    # return an interpolator: interpolate y from x
    def interpolator(self, x, y, order=1):
        # sort according to the argument
        sorted = self.sort(x)
        if self.errors is not None:
            return interpolate.UnivariateSpline(sorted[x], sorted.errors[y], k=order, s=0)
        else:
            return interpolate.UnivariateSpline(sorted[x], sorted[y], k=order, s=0)
        
def load_csv(filepath, indices=[], has_header=True, use_header=False, **csv_params):
# read data from a csv file, assuming no error values are recorded
# indices = [(row_index1,variable1), ...]
    with open(filepath, "r", newline='') as f:
        reader = csv.reader(f,csv_params)
        # Read the header row if applicable
        if has_header:
            row = next(reader)
            if use_header:
                indices=enumerate(row)
        # prepare the temporary lists for reading the data
        data_lists={}
        for (i,key) in indices:
            data_lists[key] = []
        # now read the data
        for row in reader:
            for (i,key) in indices:            
                try:
                    data_lists[key].append(float(row[i]))
                except ValueError:
                    data_lists[key].append(np.nan)
    
    # Convert data to the dataset format
    data_set = DataSet()
    for (i,key) in indices:
        data_set[key]=np.array(data_lists[key], dtype=np.float, copy=True)
    
    return data_set