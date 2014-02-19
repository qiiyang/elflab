import time
import visa
from elflab.devices.dmms.dmm_base import DMMBase

class Keithley2000(DMMBase):

    def __init__(self, address):
        self.address = address
        
        connected = False

    def connect(self):
        rm = visa.ResourceManager()
        self.gpib = rm.get_instrument("GPIB::{:n}".format(self.address))
        idn = str(self.gpib.ask("*idn?".encode("ASCII")), encoding="ASCII")
        if not ("KEITHLEY INSTRUMENTS INC.,MODEL 2000" in idn):
            raise Exception("Keithley 2000 idn string does not match")
        print("        Keithley 2000 DMM connected, GPIB={:n}.".format(self.address))
        self.connected = True
        
    def reset(self):
        if not self.connected:
            self.connect()
        self.gpib.write("*rst".encode("ASCII"))
        
    def config(self, output="vdc"):
        if not self.connected:
            self.connect()
        out=output.strip().lower()
        if out == "vdc":
            self.gpib.write("CONF:VOLT:DC".encode("ASCII"))
        else:
            raise Exeption("config unrecognised for Keithley 2000 DMM")
            
    def read(self):     # Returns (relative timestamp, reading)
        if not self.connected:
            self.connect()
        reading = str(self.gpib.ask(":read?".encode("ASCII")), encoding="ASCII")
        t = time.perf_counter()
        return(t, float(reading))
            
        
        