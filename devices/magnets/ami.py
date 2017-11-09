""" AMI Magnet Power Supplies """
import visa
import time
from .magnet_base import MagnetBase

class Model420(MagnetBase):
    def __init__(self, address):
        self.address = address
        
        self.connected = False
        self.H = float('nan')
        self.I = float('nan')
        
    def connect(self):
        rm = visa.ResourceManager()
        self.gpib = rm.open_resource("GPIB::{:n}".format(self.address))
        self.gpib.write("CONFigure:FIELD:UNITS 1")  # Configure the field unit to Tesla
        print("        AMI Model 420 magnet programmer connected, GPIB={:n}.".format(self.address))        
        self.connected = True
    
    def read(self): # returns (t, H/Tesla, I_magnet/A)
        err = True  # error flag for detecting GPIB error
        while err:
            try:        
                stat = str(self.gpib.query("FIELD:MAGnet?"))
                self.H = float(stat)
            except:
                pass
            else:
                err = False
            
        return (time.perf_counter(), self.H, float("nan"))
        
        


class Model430(MagnetBase):
    idn_str = "430"   # Identifier string to check
    def __init__(self, address):
        self.address = address
        
        self.connected = False
        self.H = float('nan')
        self.I = float('nan')
        
    def connect(self):
        rm = visa.ResourceManager()
        self.instrument = rm.open_resource(self.address, baud_rate = 115200, parity = visa.constants.Parity.none, data_bits = 8, stop_bits = visa.constants.StopBits.one, flow_control=visa.constants.VI_ASRL_FLOW_RTS_CTS)
        
        
        idn = self.instrument.query("*idn?")
        if (self.idn_str not in idn):
            raise Exception("AMI Model 430 magnet programmer idn string does not match")
            
        self.instrument.write("CONFigure:FIELD:UNITS 1")  # Configure the field unit to Tesla
        print("        AMI Model 430 magnet programmer connected, address={}.".format(self.address))        
        self.connected = True
    
    def read(self): # returns (t, H/Tesla, I_magnet/A)
        try:        
            stat = str(self.instrument.query("FIELD:MAGnet?"))
            self.H = float(stat)
        except:
            self.H = float("nan")
            
        return (time.perf_counter(), self.H, float("nan"))

        