""" Lockin base class """

from ..device_base import DeviceBase

class LockinBase(DeviceBase):  
    def __init__(self, address):
        raise Exception("Lockin function not implemented.")
    
    def connect(self):
        raise Exception("Lockin function not implemented.")
    
    def adjustSens(self, R): # R: current R value
        raise Exception("Lockin function not implemented.")
        
    def read(self):     # return current readings
        raise Exception("Lockin function not implemented.")
        
        
class DigitalLockinBase(LockinBase):  
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
        
class AnalogueLockinBase(LockinBase):  
    def __init__(self, dmm):
        raise Exception("Lockin function not implemented.")
    
    def connect(self):
        raise Exception("Lockin function not implemented.")
        
    def setAutoSens(self, low, high):
        raise Exception("Cannot set AutoSens for an analogue lock in")
    
    def adjustSens(self, R): # R: current R value
        raise Exception("Cannot read R for an analogue lock in")
            
    def read(self):     # return current reading
        raise Exception("Lockin function not implemented.")
        
    def setf(self, f):
        raise Exception("Cannot set frequency for an analogue lock in")