""" Simulated Thermometers """

from elflab.devices.thermometers.therm_base import ThermBase
import time

class StepTherm(ThermBase):
    """ A fake thermometer returns stepped increasing temperature and zero I, V """
    def __init__(self, initialT=300., step=-1.):
        self.T = initialT
        self.step = step
    
    def read(self):
        self.T += self.step
        t = time.perf_counter()
        return (t, 0., 0., self.T)

    