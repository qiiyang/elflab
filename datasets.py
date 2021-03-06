######################################################################################################
# Defines the DataSet class and various creation / manipulation methods
######################################################################################################
import csv

import elflab.abstracts as abstracts

import scipy.interpolate as interpolate
import numpy as np

class DataSet(abstracts.DataSetBase):
    def __init__(self, *args, **kwargs):
        super(DataSet, self).__init__(*args, **kwargs)
        self.sorted_views = {}
        if len(self) > 0:
            self.length = -1
            for key in self:
                if self.length < 0:
                    self.length = self[key].shape[0]
                # Check entry length
                if (self[key].shape[0] != self.length):
                    raise IndexError("[elflab.DataSet.__init__] lengths of entries do not match")
                # Check error entry length
                if (self.errors is not None) and (self.errors[key].shape[0] != self.length):
                    raise IndexError("[elflab.DataSet.__init__] lengths of entries do not match")
        else:
            self.length = 0
        self.titles={key:key for key in self}
        
    # Update the fields after data change
    def update(self):
        self.sorted_views = {}
        if len(self) > 0:
            self.length = -1
            for key in self:
                if self.length < 0:
                    self.length = self[key].shape[0]
                # Check entry length
                if (self[key].shape[0] != self.length):
                    raise IndexError("[elflab.DataSet.__init__] lengths of entries do not match")
                # Check error entry length
                if (self.errors is not None) and (self.errors[key].shape[0] != self.length):
                    raise IndexError("[elflab.DataSet.__init__] lengths of entries do not match")
        else:
            self.length = -1
        for key in self:
            if key not in self.titles:
                self.titles[key] = key
        
        
    # Create an empty dataset with identical variables
    def empty(self):
        new_set = DataSet([(key, np.empty((0,), dtype=np.float)) for key in self])
        if self.errors is not None:
            new_set.errors = {key:np.empty((0,), dtype=np.float) for key in self}
        new_set.titles = self.titles.copy()
        new_set.length = 0
        return new_set
        
    # Define how exactly a dataset is to be copied, while not over-writing the copy() method
    def duplicate(self):
        new_set = DataSet([(key,self[key].copy()) for key in self])
        if self.errors is not None:
            new_set.errors = {key: self.errors[key].copy() for key in self}
        new_set.titles = self.titles.copy()
        return new_set
        
    # return a sorted copy
    def sort(self, key):
        # compute sorted indices
        if key in self.sorted_views:
            sorted = self.sorted_views[key]
        else:
            indices = np.argsort(self[key], kind='quicksort')
            sorted = DataSet([(k,self[k][indices]) for k in self])
            if self.errors is not None:
                sorted.errors = {k:self.errors[k][indices] for k in self}
            self.sorted_views[key] = sorted
            sorted.sorted_views = self.sorted_views
            sorted.titles = self.titles
        return sorted
        
    # return an interpolator: interpolate y from x
    def interpolator(self, x, y, order=1):
        # sort according to the argument
        sorted = self.sort(x)
        return interpolate.UnivariateSpline(sorted[x], sorted[y], k=order, s=0)
            
    # return an interpolator: interpolate err^2(y) from x
    def error2_interpolator(self, x, y, order=1):
        # sort according to the argument
        sorted = self.sort(x)
        if self.errors is not None:
            return interpolate.UnivariateSpline(sorted[x], np.square(sorted.errors[y]), k=order, s=0)
        else:
            raise Exception("Errors not defined.")
    
    # return a masked version of self by using numpy indexing
    def mask(self, indices):
        newset = DataSet({key: self[key][indices] for key in self})
        if self.errors is not None:
            newset.errors = {key: self.errors[key][indices] for key in self}
        newset.update()
        return newset
    
        
def load_csv(filepath, column_mapping, error_column=0, has_header=True, use_header=True, **csv_params):
    """read data from a csv file, assuming no error values are recorded
    column_mapping = {column_index1: variable_name1, ...}, has to be specified by user for all columns to read
    If use_header == True, then the headers will be read as the full titles of the variables
    error_column > 0 if the file contains error information on the values, and stored starting at error_column in the same order of value columns."""              
    # prepare the temporary lists for reading the data
    n_column = len(column_mapping)
    data_lists = {column_mapping[i]:[] for i in column_mapping}
    if error_column > 0:
        error_lists = {column_mapping[i]:[] for i in column_mapping}      
    # read the file
    with open(filepath, "r", newline='') as f:  
        reader = csv.reader(f,**csv_params)
        # Read the header row if applicable
        if has_header:
            row = next(reader)
            if use_header:
                titles = {column_mapping[i]: row[i] for i in column_mapping}
            else:
                titles = {column_mapping[i]: column_mapping[i] for i in column_mapping}
        else:
            titles = {column_mapping[i]: column_mapping[i] for i in column_mapping}
        # now read the data
        for row in reader:
            if len(row) >= n_column:
                for i in column_mapping:   
                    key = column_mapping[i]
                    try:
                        data_lists[key].append(float(row[i]))
                    except ValueError:
                        data_lists[key].append(np.nan)
                    
                    if error_column > 0:
                        try:
                            error_lists[key].append(float(row[i+error_column]))
                        except ValueError:
                            error_lists[key].append(np.nan)
            else:
                print ("WARNING: Too few columns read, skipping row.")
                    
    
    # Convert data to the dataset format
    data_set = DataSet([(key, np.array(data_lists[key], dtype=np.float)) for key in data_lists])
    data_set.titles = titles
    if error_column > 0:
        data_set.errors = {key: np.array(error_lists[key], dtype=np.float) for key in data_lists}
    return data_set
    
def save_csv(dataset, filepath, columns=None, format_string="{:.10g}", write_header=True, **csv_params):
    """write data to a csv file
    columns: a list of variables to write, write all variables if None
    header is the header row in list format, including the errors"""
    
    if columns is None:
        N = len(dataset)
        columns = [key for key in dataset]
    else:
        N = len(columns)
    
    # create an empty row
    if dataset.errors is None:
        row = ['' for i in range(N)]
    else:
        row = ['' for i in range(2*N)]
        
    # write to file
    with open(filepath, "w", newline='') as f:  
        writer = csv.writer(f, **csv_params)
        # write header line
        if write_header:
            for i in range(N):
                row[i] = columns[i]
            if dataset.errors is not None:
                for i in range(N):
                    row[i+N] = "error({})".format(columns[i])
            writer.writerow(row)
        # write data lines
        for i in range(dataset.length):
            for j in range(N):
                key = columns[j]
                row[j] = format_string.format(dataset[key][i])
            if dataset.errors is not None:
                for j in range(N):
                    key = columns[j]
                    row[j+N] = format_string.format(dataset.errors[key][i])
            writer.writerow(row)
    
# Merge two datasets, currently errors are ignored
def merge(dataset1, dataset2):
    # Firstly check whether keys match
    if set(dataset1.keys()) != set(dataset2.keys()):
        raise Error("The datasets to merge have different keys!")
    newset = DataSet({key: np.concatenate((dataset1[key], dataset2[key])) for key in dataset1})
    if (dataset1.errors is not None) and (dataset2.errors is not None):
        newset.errors = DataSet({key: np.concatenate((dataset1.errors[key], dataset2.errors[key])) for key in dataset1})
    newset.update()    
    return newset
    
def downsample(dataset, size, method=np.nanmean, error_est=None):
    """Down sampling the dataset by a sampling function "method"
    size is the number of data points per sample
    new errors are estimated with the function "error_est"
    return the down-sampled dataset"""
    # If the old set has errors undefined, set all errors as zero
    if (error_est is not None) and (dataset.errors is None):
        dataset.errors = {key:np.zeros((dataset.length,), dtype=np.float) for key in dataset}
    # prepare an empty new set
    new_length = dataset.length // size
    newset = DataSet([(key, np.empty((new_length,), dtype=np.float)) for key in dataset])
    if error_est is None:
        newset.errors = None
    else:
        newset.errors = {key: np.empty((new_length,), dtype=np.float) for key in dataset}
    
    # calculate the values in the new set
    for key in dataset:
        for i in range(new_length-1):
            newset[key][i] = method(dataset[key][i*size:(i+1)*size])
            if error_est is not None:
                newset.errors[key][i] = error_est(dataset[key][i*size:(i+1)*size], dataset.errors[key][i*size:(i+1)*size])
        newset[key][new_length-1] = method(dataset[key][(new_length-1)*size:dataset.length])
        if error_est is not None:
            newset.errors[key][new_length-1] = error_est(dataset[key][(new_length-1)*size:dataset.length], dataset.errors[key][(new_length-1)*size:dataset.length])
    return newset


    
def consolidate(dataset, key, window_size, method, error_est=None):
    """consolidate the dataset by method similar values in the variable "key",  method near by data points by function "method"
    window_size is the threshold defining similarity
    new errors are estimated with the function "error_est"
    return the consolidated dataset"""
    
    # sort the dataset
    sorted = dataset.sort(key)
    
    # If the old set has errors undefined, set all errors as zero
    if (sorted.errors is None) and (error_est is not None):
        sorted.errors = {k:np.zeros((sorted.length,), dtype=np.float) for k in sorted}
        
        
    # make the list representation of the consolidated data
    datalists = {}
    for k in sorted:
        datalists[k] = []
        
    if error_est is not None:
        errorlists = {}
        for k in sorted:
            errorlists[k] = []
        
    l = sorted.length
    i = 0
    j = 0
    
    # calculate the new data
    while j < l:
        i = j
        j = i + 1
        while (j < l) and (sorted[key][j] - sorted[key][i] <= window_size):
            j += 1
        for k in sorted:
            datalists[k].append(method(sorted[k][i:j]))
            if error_est is not None:
                errorlists[k].append(error_est(sorted[k][i:j], sorted.errors[k][i:j]))
        
    # Make the new set
    newset = DataSet([(k, np.array(datalists[k], dtype=np.float)) for k in dataset])
    if error_est is not None:
        newset.errors = {k: np.array(errorlists[k], dtype=np.float) for k in dataset}
    else:
        newset.errors = None

    return newset