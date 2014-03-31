import numpy as np

import elflab.abstracts as abstracts
import scipy.interpolate as interpolate

class DataSet(abstracts.DataSetBase):
    def __init__(self, args=[]):
        super(DataSet, self).__init__(args)
        self.sorted_views = {}
        
    # Create an empty dataset with identical variables
    def empty(self):
        new_set = DataSet()
        for key in self:
            new_set[key] = None
        return new_set
        
    # Define how exactly a dataset is to be copied, while not over-writing the copy() method
    def duplicate(self):
        new_set = DataSet()
        for key in self:
            new_set[key] = self[key].copy()
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
            sorted.sorted_views[key] = sorted
        return sorted
        
    # return an interpolator: interpolate y from x
    def interpolator(self, x, y, order=1):
        # sort according to the argument
        sorted = self.sort(x)
        return interpolate.UnivariateSpline(sorted[x], sorted[y], k=order, s=0)
        