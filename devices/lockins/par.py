import time
import visa
from elflab.devices.lockins.lockin_base import AnalogueLockinBase

class PAR124A(AnalogueLockinBase):  
    def __init__(self, dmm, sens, theta, f, Vout, transformer=False):
        self.dmm = dmm
        self.sens = sens
        self.theta = theta
        self.f = f
        self.Vout = Vout
        if transformer:
            self.sens /= 100.
        self.connected = False
    
    def connect(self):
        self.dmm.connect()
        print("        SR830 lock-in amplifier, read through dmm")        
        self.connected = True
    
    def read(self):     # return (t, X, Y, R, theta, f, Vout)
        t, dmm_V = self.dmm.read()
        return (t, dmm_V / 10. * self.sens, float("nan"), float("nan"), self.theta, self.f, self.Vout)