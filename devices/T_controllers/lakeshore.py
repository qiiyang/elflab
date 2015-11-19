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