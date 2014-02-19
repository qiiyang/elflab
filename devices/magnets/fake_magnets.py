""" Simulated Thermometers """

from .magnet_base import MagnetBase
import time

class StepMagnet(MagnetBase):
    """ A fake magnet returns stepped increasing H and zero I"""
    def __init__(self, initialH=0., step=1.e-3):
        self.H = initialH
        self.step = step
    
    def read(self):
        self.H += self.step
        return (time.perf_counter(), self.H, 0.)
        
    def connect(self):
        pass


class ConstMagnet(MagnetBase):
    """ A fake magnet returns constant H and I"""
    def __init__(self, H=0., I=0.):
        self.H = H
        self.I = I
    
    def read(self):
        return (time.perf_counter(), self.H, self.I)
        
    def connect(self):
        pass

        