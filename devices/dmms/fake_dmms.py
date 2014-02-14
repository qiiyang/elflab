""" Simulated DMMs """

from .dmm_base import DeviceBase

class ConstDMM(DeviceBase):
    """ A fake DMM only reads constant value """
    def __init__(self, reading=0.):
        self.reading = reading
    
    def read(self):
        return self.reading

        