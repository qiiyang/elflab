""" Common definitions / whatever shared for all Janis He-3 related scripts
"""
import time
import math
import threading

import tkinter as tk
from tkinter import ttk

from elflab import uis
from elflab.devices.T_controllers.lakeshore import Lakeshore340

import elflab.abstracts as abstracts
import elflab.dataloggers.csvlogger as csvlogger

from elflab.devices.lockins import fake_lockins, par
from elflab.devices.magnets import fake_magnets
from elflab.devices.dmms import keithley

T_RUO = 20. # Temperature below which to use RuO readings

GPIB_LAKESHORE340 = 11
GPIB_DMM = 19

# Conversion between data names and indices and labels etc.

VAR_ORDER = ["n", "t", "T_sample", "H", "T_A", "T_B", "T_sorb", "T_1K", "R1", "R2", "X1", "Y1", "f1", "Vex1", "X2", "Y2", "f2", "Vex2"]

# Everything in SI

VAR_DESC = {
            "n": "no. of data points",
            "t": "timestamp, absolute, in s",
            "T_sample": "sample temperature / K",
            "H": "magnetic field, in T", 
            "T_A": "sample temperature: RuO",
            "T_B": "sample temperature: Si diode",
            "T_sorb": "sorb temperature / K", 
            "T_1K": "1K Pot temperature / K",
            "R1": "Resistance of channel 1 / Ohm",
            "R2": "Resistance of channel 2 / Ohm",
            "X1": "Lockin X on ch 1 / V", 
            "Y1": "Lockin Y on ch 1 / V",
            "f1": "Lockin frequency on ch 1 / Hz",
            "Vex1": "Lockin sine output on ch 1 / V",
            "X2": "Lockin X on ch 2 / V", 
            "Y2": "Lockin Y on ch 2 / V",
            "f2": "Lockin frequency on ch 2 / Hz",
            "Vex2": "Lockin sine output on ch 2 / V"
            }
            
VAR_TITLES = {
            "n": "n",
            "t": "t / s",
            "T_sample": "T_sample / K",
            "T_A": "T_A / K",
            "T_B": "T_B / K",
            "T_sorb": "T_sorb / K", 
            "T_1K": "T_1K / K",
            "H": "H / T",
            "R1": "R1 / Ohm",
            "R2": "R2 / Ohm",
            "X1": "X1 / V", 
            "Y1": "Y1 / V",
            "f1": "f1 / Hz",
            "Vex1": "Vex1 / V",
            "X2": "X2 / V", 
            "Y2": "Y2 / V",
            "f2": "f2 / Hz",
            "Vex2": "Vex2 / V"
            }
            
VAR_FORMATS = {
            "n": "{:n}",
            "t": "{:.8f}",
            "T_sample": "{:.10e}",
            "T_A": "{:.10e}",
            "T_B": "{:.10e}",
            "T_sorb": "{:.10e}", 
            "T_1K": "{:.10e}",
            "H": "{:.10e}",
            "R1": "{:.10e}",
            "R2": "{:.10e}",
            "X1": "{:.10e}",
            "Y1": "{:.10e}",
            "f1": "{:.10e}",
            "Vex1": "{:.10e}",
            "X2": "{:.10e}", 
            "Y2": "{:.10e}",
            "f2": "{:.10e}",
            "Vex2": "{:.10e}"
            }
            
VAR_INIT = {
            "n": 0,
            "t": 0.,
            "T_sample": 0.,
            "T_A": 0.,
            "T_B": 0.,
            "T_sorb": 0., 
            "T_1K": 0.,
            "H": 0.,
            "R1": 0.,
            "R2": 0.,
            "X1": 0.,
            "Y1": 0.,
            "f1": 0.,
            "Vex1": 0.,
            "X2": 0., 
            "Y2": 0.,
            "f2": 0.,
            "Vex2": 0.
            }
                 

SENS_RANGE = (0.1, 0.8)

class JanisS07GUI(uis.GenericGUI):
    def __init__(self, Kernel, Experiment, Controller=JanisS07Controller):
        super().__init__(Kernel, Experiment, Controller=Controller)
        # Control Panel Layout
            # Status
        self.c0_frame = ttk.Frame(self.controlFrame)
        self.c0_frame.grid(row=0, column=0)
        
        self.c1_frame = ttk.LabelFrame(self.controlFrame, text="Sorb Loop")
        self.c1_frame.grid(row=1, column=0, sticky="nw")
        
        self.c2_frame = ttk.LabelFrame(self.controlFrame, text="Sample Loop")
        self.c2_frame.grid(row=0, column=1, rowspan=2, sticky="nw")
        
        # Instrument Status
            # titles
        l = ttk.Label(self.c0_frame, text="sample")
        l.grid(row=1, column=0)
        l = ttk.Label(self.c0_frame, text="sorb")
        l.grid(row=2, column=0)
        l = ttk.Label(self.c0_frame, text="T / K")
        l.grid(row=0, column=1)
        l = ttk.Label(self.c0_frame, text="setp. / K")
        l.grid(row=0, column=2)
        l = ttk.Label(self.c0_frame, text="ramp")
        l.grid(row=0, column=3)
        l = ttk.Label(self.c0_frame, text="heater / \%")
        l.grid(row=0, column=4)
        
        self.c0_T1 = ttk.Label(text="", )

class JanisS07Controller(abstracts.ControllerBase):
    """Controller for s07 Janis"""
    T_MIN = 0.0
    R_MIN = 0.1
    R_MAX = 20.0
    
    DEFAULT_ASSIST_INTERVAL = 5.0
    DEFAULT_ASSIST_STEP = 0.05
    DEFAULT_ASSIST_THRESHOLD = 0.8
    ASSIST_MAX_T = 40.0
    
    def __init__(self, kernel):
        self.kernel = kernel
        self.lakeshore = kernel.experiment.lakeshore
        self.instrument_lock = kernel.instrument_lock
        self.data_lock = kernel.data_lock
        
        # sort stepping parameters for assisting sample ramping
        self.ramp_assist_threshold = self.DEFAULT_ASSIST_THRESHOLD 
        self.ramp_assist_interval = self.DEFAULT_ASSIST_INTERVAL     # in second
        self.ramp_assist_step = self.DEFAULT_ASSIST_STEP    # in Kelvin
        
        self.end_assist = threading.Event()
        
        # Initialise the assist thread
        self.assist_thread = threading.Thread(target=None)
        self.assist_thread.start()
        
    # Read the status of the T_controller
    # returns (T1, SETP1, rampst1, Heater1, T2, SETP2, rampst2, HEATERs)
    def get_status(self):
        if self.kernel.flag_pause or self.kernel.flag_stop or self.kernel.flag_quit:
            with self.instrument_lock:
                T1 = self.lakeshore.read("C")[1]
                T2 = self.lakeshore.read("A")[1]
        else:
            with self.data_lock:
                T1 = self.kernel.current_values["T_sorb"]
                T2 = self.kernel.current_values["T_A"]
        with self.instrument_lock:
            setp1 = self.lakeshore.get_setp(1)
            setp2 = self.lakeshore.get_setp(2)
            heater1 = self.lakeshore.get_heater(1)
            heater2 = self.lakeshore.get_heater(2)
            rampst1 = self.lakeshore.get_rampst(1)
            rampst2 = self.lakeshore.get_rampst(2)
        return (T1, setp1, rampst1, heater1, T2, setp2, rampst2, heater2)
        
    def heater_off(self, loop):
        with self.instrument_lock:
            self.lakeshore.set_ramp(loop, 0, R_MIN)
            self.lakeshore.set_setp(loop, T_MIN)
    
    def step(self, loop, T):
        with self.instrument_lock:
            self.lakeshore.set_ramp(loop, 0, R_MIN)
            self.lakeshore.set_setp(loop, T_MIN)
        
    def ramp1(self, T, r):
        (T1, setp1, rampst1, heater1, T2, setp2, rampst2, heater2) = self.get_status()
        self.step(1, T1)
        with self.instrument_lock:
            self.lakeshore.set_ramp(1, 1, r)
            self.lakeshore.set_setp(1, T)
            
    
    def ramp2(self, T, r):
        # stop the old assist thread
        self.end_assist.set()
        self.assist_thread.join(timeout=0.1)
        # set ramping
        (T1, setp1, rampst1, heater1, T2, setp2, rampst2, heater2) = self.get_status()
        self.step(2, T2)
        with self.instrument_lock:
            self.lakeshore.set_ramp(2, 1, r)
            self.lakeshore.set_setp(2, T)
        # starting the assist thread
        self.assist_thread = threading.Thread(target=self.ramp_assist)
        self.assist_thread.start()
    
    # Change the parameters for ramping assist
    def set_assist(self, threshold, interval, step):
        self.ramp_assist_threshold = threshold
        self.ramp_assist_interval = interval     # in second
        self.ramp_assist_step = step    # in Kelvin
        
    def ramp_assist(self):
        while self.end_assist.wait(timeout=self.ramp_assist_interval):
            (T1, setp1, heater1, T2, setp2, heater2) = self.get_status()
            if heater2 > self.ramp_assist_threshold:
                self.step(1, T1+self.ramp_assist_step)
            if T1 >= self.ASSIST_MAX_T:
                self.end_assist.set()
        
    def terminate(self):
        self.end_assist.set()
        self.assist_thread.join(timeout=0.1)
                
class JanisS07TwoLockinAbstract(abstracts.ExperimentBase):
    # "Public" Variables
    title = "Janis S07 He-3: with Two Lock In Amplifiers"
    
    default_params = {
        "R_series1 / Ohm": 'no entry',
        "R_series2 / Ohm": 'no entry'
    }
    
    var_order = VAR_ORDER.copy()    # order of variables
    var_titles = VAR_TITLES.copy()    # matching short names with full titles  = {e.g "H": "$H$ (T / $\mu_0$)"}
    format_strings = VAR_FORMATS.copy()   # Format strings for the variables
    
    plotXYs = [
            [("T_sample", "R1"), ("T_sample", "R2")],
            [("t", "T_sample"), ("t", "T_1K")]
            ]
    
    default_comments = ""
    def __init__(self, params, filename, lockin1, lockin2, magnet):
        # Define the temperature controllers
        self.lakeshore = Lakeshore340(GPIB_LAKESHORE340)
    
        # Save parameters
        self.lockin1 = lockin1
        self.R_series1 = float(params["R_series1 / Ohm"])
        self.lockin2 = lockin2
        self.R_series2 = float(params["R_series2 / Ohm"])
        self.magnet = magnet
        
        # Initialise variables
        self.current_values = VAR_INIT.copy()   # = {"name": "value"}
        # create a csv logger
        self.logger = csvlogger.Logger(filename, self.var_order, self.var_titles, self.format_strings)
        
    
    def start(self):
        # Connect to instruments
        self.lakeshore.connect()
        self.lockin1.connect()
        self.lockin2.connect()
        self.magnet.connect()
        
        if self.lockin1.is_digital:
            self.lockin1.setAutoSens(*SENS_RANGE)
        if self.lockin2.is_digital:
            self.lockin2.setAutoSens(*SENS_RANGE)
        
        # Reset counter and timer
        self.n = 0
        self.t0 = time.perf_counter()
        # Start the csv logger
        self.logger.start()
        
    def measure(self):
        self.currentValues["n"] += 1
        t,self.currentValues["T_A"] = self.lakeshore.read("A")
        t,self.currentValues["T_B"] = self.lakeshore.read("B")
        t,self.currentValues["T_sorb"] = self.lakeshore.read("C")
        t,self.currentValues["T_1K"] = self.lakeshore.read("D")
        
        self.currentValues["t"] = t - self.t0
        
        if math.isnan(self.currentValues["T_B"]) or (self.currentValues["T_B"] < T_RUO):
            self.currentValues["T_sample"] = self.currentValues["T_A"]
        else:
            self.currentValues["T_sample"] = self.currentValues["T_B"]
        
        t,self.currentValues["H"],t = self.magnet.read()
        t,self.currentValues["X1"],self.currentValues["Y1"],t,t,self.currentValues["f1"],self.currentValues["Vex1"] = self.lockin1.read()
        t,self.currentValues["X2"],self.currentValues["Y2"],t,t,self.currentValues["f2"],self.currentValues["Vex2"] = self.lockin2.read()
        self.currentValues["R1"] = self.currentValues["X1"] / self.currentValues["Vex1"] * self.R_series1
        self.currentValues["R2"] = self.currentValues["X2"] / self.currentValues["Vex2"] * self.R_series2
        
    def log(self, dataToLog):
        self.logger.log(dataToLog)
        
    # A perpetual sequence
    def sequence(self):
        while True:
            yield True
        
    def finish(self):
        self.logger.finish()

class JanisS07PAR124MI(JanisS07TwoLockinAbstract):
    # "Public" Variables
    title = "Janis S07 He-3: MI measurements with PAR 124"
    
    default_params = {
        "R_series1 / Ohm": 'no entry',
        "R_series2 / Ohm": 'no entry',
        "sens / V": 'no entry',
        "theta / degrees": 'no entry',
        "f / Hz": 'no entry',
        "Vout / V": 'no entry',
        "transformer mode": '0 for False'
    }
    
    var_order = VAR_ORDER.copy()    # order of variables
    var_titles = VAR_TITLES.copy()    # matching short names with full titles  = {e.g "H": "$H$ (T / $\mu_0$)"}
    format_strings = VAR_FORMATS.copy()   # Format strings for the variables
    
    plotXYs = [
            [("T_sample", "X1"), ("t", "T_sample")],
            [("t", "T_1K"), ("t", "T_sorb")]
            ]
    
    default_comments = ""
    
    def __init__(self, params, filename):   
        sens = float(params["sens / V"])
        theta = float(params["theta / degrees"])
        f = float(params["f / Hz"])
        Vout = float(params["Vout / V"])
        transformer = (int(params["transformer mode"]) != 0)
        
        dmm = keithley.Keithley196(GPIB_DMM)
        lockin1 = par.PAR124A(dmm, sens=sens, theta=theta, f=f, Vout=Vout, transformer=True)
        lockin2 = fake_lockins.ConstLockin(float("nan"))
        
        magnet = fake_magnets.ConstMagnet()
        
        super().__init__(params, filename, lockin1, lockin2, magnet)