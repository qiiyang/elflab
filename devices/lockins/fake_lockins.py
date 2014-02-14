""" Simulated Lockin Amplifiers """

from .lockin_base import LockinBase
from math import sin, cos

class SinCosLockin(LockinBase):
    """ X=sin(wn), Y = cos(wn) """
    def __init__(self, w=0.03):
        self.w = w      # angular frequency
        self.phi = 0.   # phase
    
    def readXY(self): 
        x = sin(self.phi)
        y = cos(self.phi)
        self.phi += self.w
        return (x, y)

        