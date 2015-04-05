import time
import visa
from elflab.devices.T_controllers.T_controller_base import TControllerBase

class Lakeshore332(TControllerBase):  
    def __init__(self, address):
        self.address = address
        
        self.connected = False
        self.autosense = False
    
    def connect(self):
        rm = visa.ResourceManager()
        self.gpib = rm.get_instrument("GPIB::{:n}".format(self.address))
        idn = str(self.gpib.ask("*idn?".encode("ASCII")), encoding="ASCII")
        if not ("LSCI,MODEL332S" in idn):
            raise Exception("Lakeshore Model 332 temperature controller idn string does not match")
        self.gpib.write("*CLS?".encode("ASCII"))
        print("        Lakeshore Model 332 temperature controller, GPIB={:n}.".format(self.address))        
        self.connected = True
    
    def read(self, ch):     # return (t, T) for the specified channel
        reading = str(self.gpib.ask("KRDG? {}".format(ch).encode("ASCII")), encoding="ASCII")
        t = time.perf_counter()
        T = float(reading)
        return (t, T)