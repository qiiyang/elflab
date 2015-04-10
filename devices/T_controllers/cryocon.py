import time
import visa
from elflab.devices.T_controllers.T_controller_base import TControllerBase

class Cryocon32B(TControllerBase):  
    def __init__(self, address):
        self.address = address
        
        self.connected = False
        self.autosense = False
    
    def connect(self):
        rm = visa.ResourceManager()
        self.gpib = rm.get_instrument("GPIB::{:n}".format(self.address))
        idn = str(self.gpib.ask("*idn?".encode("ASCII")), encoding="ASCII")
        if not ("Cryocon Model 32" in idn):
            raise Exception("Cryocon Model 32 temperature controller idn string does not match")
        self.gpib.write("*CLS?".encode("ASCII"))
        print("        Cryocon Model 32 temperature controller, GPIB={:n}.".format(self.address))        
        self.connected = True
    
    def read(self, ch):     # return (t, T) for the specified channel
        reading = str(self.gpib.ask("INPUT? {}".format(ch).encode("ASCII")), encoding="ASCII")
        t = time.perf_counter()
        try:
            T = float(reading)
        except ValueError:
            T = float("nan")
        return (t, T)