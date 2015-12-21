import time
import visa
from elflab.devices.T_controllers.T_controller_base import TControllerBase

class Lakeshore332(TControllerBase):  
    def __init__(self, address):
        self.address = address
        
        self.connected = False
    
    def connect(self):
        rm = visa.ResourceManager()
        self.gpib = rm.open_resource("GPIB::{:n}".format(self.address))
        idn = self.gpib.query("*idn?")
        if not ("LSCI,MODEL332S" in idn):
            raise Exception("Lakeshore Model 332 temperature controller idn string does not match")
        self.gpib.write("*CLS?")
        print("        Lakeshore Model 332 temperature controller, GPIB={:n}.".format(self.address))        
        self.connected = True
    
    def read(self, ch):     # return (t, T) for the specified channel
        if not self.connected:
            self.connect()
        reading = self.gpib.query("KRDG? {}".format(ch))
        t = time.perf_counter()
        try:
            T = float(reading)
        except ValueError:
            T = float("nan")
        return (t, T)
        
class Lakeshore340(TControllerBase):  
    def __init__(self, address):
        self.address = address
        
        self.connected = False
    
    def connect(self):
        rm = visa.ResourceManager()
        self.gpib = rm.open_resource("GPIB::{:n}".format(self.address))
        idn = self.gpib.query("*idn?")
        if not ("LSCI,MODEL340" in idn):
            raise Exception("Lakeshore Model 340 temperature controller idn string does not match")
        self.gpib.write("*CLS?")
        print("        Lakeshore Model 340 temperature controller, GPIB={:n}.".format(self.address))        
        self.connected = True
    
    def read(self, ch):     # return (t, T) for the specified channel
        if not self.connected:
            self.connect()
        reading = self.gpib.query("KRDG? {}".format(ch))
        t = time.perf_counter()
        try:
            T = float(reading)
        except ValueError:
            T = float("nan")
        return (t, T)
        
    def set_setp(self, loop, T):   # change the set point of a loop
        if not self.connected:
            self.connect()
        self.gpib.write("SETP {:d},{:.5E}".format(loop, T))
    
        
    def get_setp(self, loop):   # change the set point of a loop
        if not self.connected:
            self.connect()
        s = self.gpib.query("SETP? {:d}".format(loop))
        try:
            v = float(s)
        except:
            v = float("nan")
        return v
        
        
    def set_ramp(self, loop, on, r):    # set the ramp state, and rate of a loop
        if not self.connected:
            self.connect()
        self.gpib.write("RAMP {:d},{:d},{:.4g}".format(loop, on, r))
        
    def get_ramp(self, loop):    # get the ramp on/off state
        if not self.connected:
            self.connect()
        s = self.gpib.query("RAMP? {:d}".format(loop))
        try:
            v = int(s)
        except:
            v = -1
        return v
    
    def get_heater(self, loop):  # get the heater readings
        if loop == 1:
            s = self.gpib.query("HTR? 1")
        else:
            s = self.gpib.query("AOUT? 2")
            
        try:
            v = float(s)
        except:
            v = float("nan")
        return v
        