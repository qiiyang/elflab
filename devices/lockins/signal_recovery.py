import time
import visa
from elflab.devices.lockins.lockin_base import DigitalLockinBase

class Model7124(DigitalLockinBase):  
    def __init__(self, address):
        self.address = address
        
        self.connected = False
        self.autosense = False
    
    def connect(self):
        rm = visa.ResourceManager()
        self.inst = rm.open_resource(self.address)     
        self.connected = True
        print("        Signal Recovery Model 7124 lock-in amplifier, address={}.".format(self.address))     
        
    
    def read(self):     # return (t, X, Y, R, theta, f, Vout)
        if not self.connected:
            self.connect()
            
        try:
            snap = self.inst.query("XY.").split('\n')[0]
            X, Y = (float(v) for v in snap.split(','))
        except:
            X = float("nan")
            Y = float("nan")
        
        try:
            snap = self.inst.query("MP.").split('\n')[0]
            R, theta = (float(v) for v in snap.split(','))
        except:
            R = float("nan")
            theta = float("nan")
        
        try:
            snap = self.inst.query("OF.").split('\n')[0]
            f = float(snap)
        except:
            f = float("nan")
        
        try:
            snap = self.inst.query("OA.").split('\n')[0]
            Vout = float(snap)
        except:
            Vout = float("nan")
        
        t = time.perf_counter()
        return (t, X, Y, R, theta, f, Vout)