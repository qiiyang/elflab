""" Simulated Thermometers """

from .magnet_base import MagnetBase

class StepMag(MagnetBase):
    """ A fake magnet returns stepped increasing H and zero I, V """
    def __init__(self, initialH=0., step=1.e-3):
        self.H = initialH
        self.step = step
    
    def read(self):
        self.H += self.step
        return (0., self.H)

        