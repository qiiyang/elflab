import time
import visa
import string
from elflab.devices.dmms.dmm_base import DMMBase

class HP3478(DMMBase):
    def __init__(self, address):
        self.address = address
        self.connected = False

    def connect(self):
        rm = visa.ResourceManager()
        self.gpib = rm.open_resource("GPIB::{:n}".format(self.address))
        print("        HP3478 DMM connected, GPIB={:n}.".format(self.address))
        self.connected = True
 
    def read(self):     # Returns (relative timestamp, reading)
        if not self.connected:
            self.connect()
        try:
            reading = self.gpib.read()
        except Exception:
            reading = "NaN"
        t = time.perf_counter()
        try:
            v = float(reading)
        except ValueError:
            v = float("NaN")
        return(t, float(reading))

        