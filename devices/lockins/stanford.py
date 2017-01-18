import time
import visa
from elflab.devices.lockins.lockin_base import DigitalLockinBase

class SR830(DigitalLockinBase):  
    idn_str = "SR830"   # Identifier string to check
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
        self.gpib = rm.open_resource("GPIB::{:n}".format(self.address))
        idn = self.gpib.query("*idn?")
        if (self.idn_str not in idn):
            raise Exception("SR830 lock-in amplifier idn string does not match")
        self.gpib.write("*CLS?")
        print("        SR830 lock-in amplifier, GPIB={:n}.".format(self.address))        
        self.connected = True
    
    def setAutoSens(self, low, high):
        self.lowSens = low
        self.highSens = high
        self.autosense = True
    
    def adjustSens(self, R): # R: current R value
        i = int(self.gpib.query("sens?"))
        sens = self.sensList[i]
        overloaded = int(self.gpib.query("LIAS?")) % 8
        
        if (i < 26) and (overloaded or (abs(R) / sens > self.highSens)):
            self.gpib.write("sens {:n}".format(i+1))
        elif (i > 0) and (overloaded or (abs(R) / sens < self.lowSens)):
            self.gpib.write("sens {:n}".format(i-1))
    
    def setf(self, f):
        self.gpib.write("FREQ {:.4f}".format(f))
        fnew = float(self.gpib.query("FREQ?"))
        
        if (abs(fnew - f) / f <= 1.e-4) or (abs(fnew - f) <= 0.0001):
            return True
        else:
            return False
    
    def read(self):     # return (t, X, Y, R, theta, f, Vout)
        snap = str(self.gpib.query("SNAP?1,2,3,4,9"))
        t = time.perf_counter()
        (X, Y, R, theta, f) = [float(v) for v in snap.split(',')]
        
        Vout = float(self.gpib.query("SLVL?"))
        
        if self.autosense:
            self.adjustSens(R)
            
        return (t, X, Y, R, theta, f, Vout)
        
class SR844(DigitalLockinBase):  
    idn_str = "SR844"   # Identifier string to check
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
        self.gpib = rm.open_resource("GPIB::{:n}".format(self.address))
        idn = self.gpib.query("*idn?")
        if (self.idn_str not in idn):
            raise Exception("SR844 lock-in amplifier idn string does not match")
        self.gpib.write("*CLS?")
        print("        SR844 lock-in amplifier, GPIB={:n}.".format(self.address))        
        self.connected = True
    
    def setAutoSens(self, low, high):
        self.lowSens = low
        self.highSens = high
        self.autosense = True
    
    def adjustSens(self, R): # R: current R value
        i = int(self.gpib.query("sens?"))
        sens = self.sensList[i]
        overloaded = int(self.gpib.query("LIAS?")) % 8
        
        if (i < 26) and (overloaded or (abs(R) / sens > self.highSens)):
            self.gpib.write("sens {:n}".format(i+1))
        elif (i > 0) and (overloaded or (abs(R) / sens < self.lowSens)):
            self.gpib.write("sens {:n}".format(i-1))
    
    def setf(self, f):
        self.gpib.write("FREQ {:.4f}".format(f))
        fnew = float(self.gpib.query("FREQ?"))
        
        if (abs(fnew - f) / f <= 1.e-4) or (abs(fnew - f) <= 0.0001):
            return True
        else:
            return False
    
    def read(self):     # return (t, X, Y, R, theta, f, Vout)
        snap = str(self.gpib.query("SNAP?1,2,3,5,8"))
        t = time.perf_counter()
        (X, Y, R, theta, f) = [float(v) for v in snap.split(',')]
        
        
        if self.autosense:
            self.adjustSens(R)
            
        return (t, X, Y, R, theta, f, 0.)