""" Simulated DMMs """

from .dmm_base import DeviceBase
import time

class ConstDMM(DeviceBase):
    """ A fake DMM only reads constant value """
    def __init__(self, reading=0.):
        self.reading = reading
    
    def read(self):
        return (time.perf_counter(), self.reading)

        