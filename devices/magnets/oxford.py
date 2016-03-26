""" Oxford Magnet Power Supplies """

from .magnet_base import MagnetBase

class IPS120_10(MagnetBase):
    def __init__(self, address):
        self.address = address
        
        self.connected = False
        self.H = float('nan')
        self.I = float('nan')
        
    def connect(self):
        rm = visa.ResourceManager()
        self.gpib = rm.open_resource("GPIB::{:n}".format(self.address))
        print("        Oxford IPS 120-10 magnet power supply connected, GPIB={:n}.".format(self.address))        
        self.connected = True
    
    def read_field(self): # returns (t, H/Tesla, I_magnet/A)
        stat = str(self.gpib.query("X"))
        if (stat[8] == '0') or (stat[8] == '2'):    # persistent switch closed
            # use persistent values
            s = str(self.gpib.query("R18")).strip("Rr")
            self.H = float(s)
            s = str(self.gpib.query("R16")).strip("Rr")
            self.I = float(s)
        else:   # persistent switch open or not present
            # use demand / measured values
            s = str(self.gpib.query("R7")).strip("Rr")  # Demand field
            self.H = float(s)
            s = str(self.gpib.query("R2")).strip("Rr")  # Measured Current
            self.I = float(s)
            
        return (time.perf_counter(), self.H, self.I)
        

        