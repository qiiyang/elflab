""" Lockin base class """

from ..device_base import DeviceBase

class LockinBase(DeviceBase):  
    def __init__(self, address):
        raise Exception("Lockin function not implemented.")
    
    def connect(self):
        raise Exception("Lockin function not implemented.")
    
    def setAutoSens(self, low, high):
        self.lowSens = low
        self.highSens = high
        self.autosense = True
    
    def adjustSens(self, R): # R: current R value
        raise Exception("Lockin function not implemented.")
        
            
    def read(self):     # return (t, X, Y, R, theta, f, Vout)
        raise Exception("Lockin function not implemented.")
        
    def setf(self):
        raise Exception("Lockin function not implemented.")
        