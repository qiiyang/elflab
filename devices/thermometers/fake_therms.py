""" Simulated Thermometers """

from .therm_base import ThermBase

class StepTherm(ThermBase):
    """ A fake thermometer returns stepped increasing temperature and zero I, V """
    def __init__(self, initialT=300., step=-1.):
        self.T = initialT
        self.step = step
    
    def read(self):
        self.T += self.step
        return (0., 0., self.T)

        
def f():
    return 0.