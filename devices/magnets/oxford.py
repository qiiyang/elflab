""" Oxford Magnet Power Supplies """

from .magnet_base import MagnetBase

class IPS120_10(MagnetBase):
    def __init__(self, address):
        self.address = address
        
        self.connected = False
        self.H = float('nan')
        
    def connect(self):
        rm = visa.ResourceManager()
        self.gpib = rm.open_resource("GPIB::{:n}".format(self.address))
        print("        Oxford IPS 120-10 magnet power supply connected, GPIB={:n}.".format(self.address))        
        self.connected = True
    
    def read_field(self): # returns (t, H/Tesla)
        stat = str(self.gpib.query("X"))
        if (stat[8] == '0') or (stat[8] == '2'):    # persistent switch closed
            s = str(self.gpib.query("X"))
        return (time.perf_counter(), self.H, 0.)
        

        