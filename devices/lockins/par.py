import time
import visa
from elflab.devices.lockins.lockin_base import LockinBase

class PAR124A(AnalogueLockinBase):  
     def __init__(self, dmm, sens, transformer=False, theta, f, Vout):
        self.dmm = dmm
        self.sens = sens
        self.theta = theta
        self.f = f
        self.Vout = Vout
        if transformer:
            self.sense /= 100.
        self.connected = False
    
    def connect(self):
        self.dmm.connect()
        print("        SR830 lock-in amplifier, read through dmm")        
        self.connected = True
    
    def read(self):     # return (t, X, Y, R, theta, f, Vout)
        dmm_V = dmm.read()
        t = time.perf_counter()
        return (t, dmm_V / 10. * sens, float("nan"), float("nan"), self.theta, self.f, self.Vout)