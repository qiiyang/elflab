import csv
from elflab.devices.thermometers.therm_base import ThermBase
import numpy as np
import scipy.interpolate as interpolate

class SiDiode(ThermBase):

    Itherm = 10.e-6     # Standard Current
    
    # Takes a DMM object and a V-T calibration file as parameters
    # V has to be in descending order
    def __init__(self, dmm, calibration):
        self.dmm = dmm
        self.calibration = calibration
        
    def connect(self):
        self.dmm.connect()
        self.dmm.reset()
        self.dmm.config(output="vdc")
        self.calibrate(self.calibration)
        
    def calibrate(self, calibration):
        self.calibration = calibration
        listV=[]
        listT=[]
        f = open(calibration, mode="rt")
        reader = csv.reader(f)
        next(reader)
        
        for row in reader:
            listV.append(float(row[0]))
            listT.append(float(row[1]))
            
        self.Vmin = listV[0]
        self.Vmax = listV[-1]
        
        self.interpolator = interpolate.UnivariateSpline(listV, listT, s=0)
        
        print("        Lakeshore Si-diode thermometer, calibration file loaded: \"{}\"".format(calibration))
        
    def VtoT(self, V):
        return self.interpolator([V])[0]
        
    def read(self):
        t, Vtherm = self.dmm.read()
        if (Vtherm >= self.Vmin) and (Vtherm <= self.Vmax):
            T = self.VtoT(Vtherm)
        else:
            T = float("nan")
        return (t, T, self.Itherm, Vtherm)
        
        