import time
import visa
from elflab.devices.lockins.lockin_base import LockinBase

class SR830(LockinBase):  

    sensList = (2.e-9, 5.e-9, 10.e-9,
            2.e-8, 5.e-8, 10.e-8,
            2.e-7, 5.e-7, 10.e-7,
            2.e-6, 5.e-6, 10.e-6,
            2.e-5, 5.e-5, 10.e-5,
            2.e-4, 5.e-4, 10.e-4,
            2.e-3, 5.e-3, 10.e-3,
            2.e-2, 5.e-2, 10.e-2,
            2.e-1, 5.e-1, 10.e-1)
            

    def __init__(self, address):
        self.address = address
        
        self.connected = False
        self.autosense = False
    
    def connect(self):
        rm = visa.ResourceManager()
        self.gpib = rm.get_instrument("GPIB::{:n}".format(self.address))
        idn = str(self.gpib.ask("*idn?".encode("ASCII")), encoding="ASCII")
        if not ("SR830" in idn):
            raise Exception("SR830 lock-in amplifier idn string does not match")
        self.gpib.write("*CLS?".encode("ASCII"))
        print("        SR830 lock-in amplifier, GPIB={:n}.".format(self.address))        
        self.connected = True
    
    def setAutoSens(self, low, high):
        self.lowSens = low
        self.highSens = high
        self.autosense = True
    
    def adjustSens(self, R): # R: current R value
        i = int(self.gpib.ask("sens?".encode("ASCII")))
        sens = self.sensList[i]
        overloaded = int(self.gpib.ask("LIAS?".encode("ASCII"))) % 8
        
        if (i < 26) and (overloaded or (abs(R) / sens > self.highSens)):
            self.gpib.write("sens {:n}".format(i+1).encode("ASCII"))
        elif (i > 0) and (overloaded or (abs(R) / sens < self.lowSens)):
            self.gpib.write("sens {:n}".format(i-1).encode("ASCII"))
    
    def setf(self, f):
        self.gpib.write("FREQ {.4f}".format(f).encode("ASCII"))
        fnew = float(self.gpib.ask("FREQ?".encode("ASCII")))
        
        if (abs(fnew - f) / f <= 1.e-4) or (abs(fnew - f) <= 0.0001):
            return True
        else:
            return False
    
    def read(self):     # return (t, X, Y, R, theta, f, Vout)
        snap = str(self.gpib.ask("SNAP?1,2,3,4,9".encode("ASCII")), encoding="ASCII")
        t = time.perf_counter()
        (X, Y, R, theta, f) = [float(v) for v in snap.split(',')]
        
        Vout = float(self.gpib.ask("SLVL?".encode("ASCII")))
        
        if self.autosense:
            self.adjustSens(R)
            
        return (t, X, Y, R, theta, f, Vout)