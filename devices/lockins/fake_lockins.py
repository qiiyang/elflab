""" Simulated Lockin Amplifiers """

from .lockin_base import *
from math import sin, cos

class SinCosLockin(AnalogueLockinBase):
    """ X=sin(wn), Y = cos(wn) """
    def __init__(self, w=0.0003):
        self.w = w      # angular frequency
        self.phi = 0.   # phase
    
    def readXY(self): 
        x = sin(self.phi)
        y = cos(self.phi)
        self.phi += self.w
        return (x, y)

class ConstLockin(DigitalLockinBase):
    def __init__(self, reading=0.):
        self.reading = reading
    
    def connect(self):
        pass
    
    def setAutoSens(self, low, high):
        self.lowSens = low
        self.highSens = high
        self.autosense = True
    
    def adjustSens(self, R): # R: current R value
        pass        
            
    def read(self):     # return (t, X, Y, R, theta, f, Vout)
        return (self.reading, self.reading, self.reading, self.reading, self.reading, self.reading, self.reading)
        
    def setf(self):
        raise Exception("Lockin function not implemented.")  