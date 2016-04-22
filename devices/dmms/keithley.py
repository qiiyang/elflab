import time
import visa
import string
from elflab.devices.dmms.dmm_base import DMMBase

class Keithley2000(DMMBase):
    def __init__(self, address):
        self.address = address
        
        self.connected = False

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
            
        

class Keithley196(DMMBase):

    def __init__(self, address):
        self.address = address
        self.connected = False

    def connect(self):
        rm = visa.ResourceManager()
        self.gpib = rm.open_resource("GPIB::{:n}".format(self.address))
        print("        Keithley 196 DMM connected, GPIB={:n}.".format(self.address))
        self.connected = True
 
    def read(self):     # Returns (relative timestamp, reading)
        if not self.connected:
            self.connect()
        try:
            reading = self.gpib.read().lstrip(string.ascii_letters)
        except Exception:
            reading = "NaN"
        t = time.perf_counter()
        try:
            v = float(reading)
        except ValueError:
            v = float("NaN")
        return(t, float(reading))
        

class Keithley617(DMMBase):
    DELAY = 3.  # Delay in seconds after change configuration
    def __init__(self, address):
        self.address = address
        self.connected = False

    def connect(self):
        rm = visa.ResourceManager()
        self.gpib = rm.open_resource("GPIB::{:n}".format(self.address))
        self.gpib.write("XF2C0X")   # Default to resistance readings
        time.sleep(DELAY)
        print("        Keithley 617 Electrometer connected, GPIB={:n}.".format(self.address))
        self.connected = True
        
    def config(self, mode):
        if not self.connected:
            self.connect()
        out=output.strip().lower()
        if mode == "volts":
            self.gpib.write("XF0C0X")
        elif mode == "amps":
            self.gpib.write("XF1C0X")
        elif mode == "ohms":
            self.gpib.write("XF2C0X")
        elif mode == "coul":
            self.gpib.write("XF3C0X")
        else:
            raise Exeption("config unrecognised for Keithley 617 Electrometer")
        time.sleep(DELAY)
 
    def read(self):     # Returns (relative timestamp, reading)
        if not self.connected:
            self.connect()
        try:
            reading = self.gpib.read().lstrip(string.ascii_letters)
        except Exception:
            reading = "NaN"
        t = time.perf_counter()
        try:
            v = float(reading)
        except ValueError:
            v = float("NaN")
        return(t, float(reading))

        