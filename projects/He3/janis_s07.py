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
    DEFAULT_FOLDER = r"C:\Qi\data"
    DEFAULT_FN = r"mi"
    
    HEATER_LOW = 0.01   # Below which show heater off
    STAT_WIDTH = 9  # Min width in status entries
    RATE_MULTIPLIER = 1.02  # multiplier when calculating the rate based on time, to allow some margin of errors
    
    def __init__(self, Kernel, Experiment, Controller):
        super().__init__(Kernel, Experiment, Controller=Controller)
        # Control Panel Layout        
            # status
        self.c0_frame = ttk.Frame(self.controlFrame)
        self.c0_frame.grid(row=0, column=0, sticky="nswe", padx = 5, pady=5)
            # sorb
        self.c1_frame = ttk.LabelFrame(self.controlFrame, text="Sorb Control")
        self.c1_frame.grid(row=1, column=0, sticky="nsw", padx = 5, pady=5, ipadx=5, ipady=5)
            # sample
        self.c2_frame = ttk.LabelFrame(self.controlFrame, text="Sample Control")
        self.c2_frame.grid(row=0, column=1, rowspan=2, sticky="nw", padx = 5, pady=5, ipadx=5, ipady=5)
        
        # Instrument Status
            # titles
        l = ttk.Label(self.c0_frame, text="sorb")
        l.grid(row=1, column=0)
        l = ttk.Label(self.c0_frame, text="sample")
        l.grid(row=2, column=0)
        l = ttk.Label(self.c0_frame, text="T / K", width=self.STAT_WIDTH)
        l.grid(row=0, column=1)
        l = ttk.Label(self.c0_frame, text="setp. / K", width=self.STAT_WIDTH)
        l.grid(row=0, column=2)
        l = ttk.Label(self.c0_frame, text="ramp", width=self.STAT_WIDTH)
        l.grid(row=0, column=3)
        l = ttk.Label(self.c0_frame, text="heater / %", width=self.STAT_WIDTH)
        l.grid(row=0, column=4)
        
            # entries
        self.c0_T1 = ttk.Label(self.c0_frame, text="NA", foreground="blue", relief="sunken")
        self.c0_T1.grid(row=1, column=1)
        self.c0_T2 = ttk.Label(self.c0_frame, text="NA", foreground="blue", relief="sunken")
        self.c0_T2.grid(row=2, column=1)
        
        self.c0_sp1 = ttk.Label(self.c0_frame, text="NA", foreground="blue", relief="sunken")
        self.c0_sp1.grid(row=1, column=2)
        self.c0_sp2 = ttk.Label(self.c0_frame, text="NA", foreground="blue", relief="sunken")
        self.c0_sp2.grid(row=2, column=2)
        
        self.c0_ramp1 = ttk.Label(self.c0_frame, text="NA", anchor="center", foreground="white", background="dim gray", relief="sunken")
        self.c0_ramp1.grid(row=1, column=3)
        self.c0_ramp2 = ttk.Label(self.c0_frame, text="NA", anchor="center", foreground="white", background="dim gray", relief="sunken")
        self.c0_ramp2.grid(row=2, column=3)
        
        self.c0_heater1 = ttk.Label(self.c0_frame, text="NA", anchor="center", foreground="white", background="dim gray", relief="sunken")
        self.c0_heater1.grid(row=1, column=4)
        self.c0_heater2 = ttk.Label(self.c0_frame, text="NA", anchor="center", foreground="white", background="dim gray", relief="sunken")
        self.c0_heater2.grid(row=2, column=4)
        
        for child in self.c0_frame.winfo_children():
            child.grid_configure(padx=2, pady=2, sticky="nswe")
            
        # Sorb Control
        l = ttk.Label(self.c1_frame, text="set point:")
        l.grid(row=0, column=0, sticky="nw", padx=5)
        l = ttk.Label(self.c1_frame, text="rate:")
        l.grid(row=1, column=0, sticky="nw", padx=5)
        
        self.c1_sp = tk.StringVar()
        l = ttk.Entry(self.c1_frame, textvariable=self.c1_sp, width=8)
        l.grid(row=0, column=1, columnspan=4, sticky="new")
        self.c1_rate = tk.StringVar()
        l = ttk.Entry(self.c1_frame, textvariable=self.c1_rate, width=8)
        l.grid(row=1, column=1, columnspan=4, sticky="new")
        
        l = ttk.Label(self.c1_frame, text=" K")
        l.grid(row=0, column=5, sticky="nw")
        l = ttk.Label(self.c1_frame, text=" K/min")
        l.grid(row=1, column=5, sticky="nw")
        
        self.c1_button_off = ttk.Button(self.c1_frame, text="heater off", command=self.c1_heater_off)
        self.c1_button_off.grid(row=2, column=0, columnspan=2, sticky="new", padx=5, pady=5)
        
        self.c1_button_step = ttk.Button(self.c1_frame, text="step", command=self.c1_step)
        self.c1_button_step.grid(row=2, column=2, columnspan=2, sticky="new", padx=5, pady=5)
        
        self.c1_button_ramp = ttk.Button(self.c1_frame, text="ramp", command=self.c1_ramp)
        self.c1_button_ramp.grid(row=2, column=4, columnspan=2, sticky="new", padx=5, pady=5)
        
        # sample control
        l = ttk.Label(self.c2_frame, text="set point:")
        l.grid(row=0, column=0, sticky="nw", padx=5)
        l = ttk.Label(self.c2_frame, text="rate:")
        l.grid(row=1, column=0, sticky="nw", padx=5)
        
        self.c2_sp = tk.StringVar()
        l = ttk.Entry(self.c2_frame, textvariable=self.c2_sp, width=8)
        l.grid(row=0, column=1, columnspan=4, sticky="new")
        self.c2_rate = tk.StringVar()
        l = ttk.Entry(self.c2_frame, textvariable=self.c2_rate, width=8)
        l.grid(row=1, column=1, columnspan=4, sticky="new")
        
        l = ttk.Label(self.c2_frame, text=" K")
        l.grid(row=0, column=5, sticky="nw")
        l = ttk.Label(self.c2_frame, text=" K/min")
        l.grid(row=1, column=5, sticky="nw")    
        
            # Calculate rate from time:
        frame = ttk.Frame(self.c2_frame, relief="sunken")
        frame.grid(row=2, column=0, columnspan=6, sticky="new", padx=5, pady=5)
        
        l = ttk.Label(frame, text="hours")
        l.grid(row=0, column=0, sticky="new", padx=5, pady=(5,0))
        l = ttk.Label(frame, text=" minutes")
        l.grid(row=0, column=1, sticky="new", padx=5, pady=(5,0))
        
        self.c2_h = tk.StringVar()
        l = ttk.Entry(frame, textvariable=self.c2_h, width=8)
        l.grid(row=1, column=0, sticky="new", padx=5, pady=(0,10))
        self.c2_m = tk.StringVar()
        l = ttk.Entry(frame, textvariable=self.c2_m, width=8)
        l.grid(row=1, column=1, sticky="new", padx=5, pady=(0,10))   
        
        self.c2_button_calc = ttk.Button(frame, text="calc.\nrate", command=self.c2_calc_rate)
        self.c2_button_calc.grid(row=0, column=2, rowspan=2, sticky="nsew", padx=5, pady=5)        
        
        for c in range(3):
            tk.Grid.columnconfigure(frame, c, weight=1)
            
        
        
        self.c2_button_off = ttk.Button(self.c2_frame, text="heater off", command=self.c2_heater_off)
        self.c2_button_off.grid(row=3, column=0, columnspan=2, sticky="new", padx=5, pady=5)
        
        self.c2_button_step = ttk.Button(self.c2_frame, text="step", command=self.c2_step)
        self.c2_button_step.grid(row=3, column=2, columnspan=2, sticky="new", padx=5, pady=5)
        
        self.c2_button_ramp = ttk.Button(self.c2_frame, text="ramp", command=self.c2_ramp)
        self.c2_button_ramp.grid(row=3, column=4, columnspan=2, sticky="new", padx=5, pady=5)
        
        # Update ramp assist parameters
        frame = ttk.Frame(self.c2_frame, relief="sunken")
        frame.grid(row=4, column=0, columnspan=6, sticky="new", padx=5, pady=5)
        
            # spacers
        w = ttk.Frame(frame)
        w.grid(row=0, column=0, pady=2.5)
        w = ttk.Frame(frame)
        w.grid(row=4, column=0, pady=2.5)
        
        l = ttk.Label(frame, text="threshold:  ")
        l.grid(row=1, column=0, sticky="nw", padx=5)
        l = ttk.Label(frame, text="step size:  ")
        l.grid(row=2, column=0, sticky="nw", padx=5)
        l = ttk.Label(frame, text="check every:  ")
        l.grid(row=3, column=0, sticky="nw", padx=5)
        
        self.c2a_threshold = tk.StringVar()
        self.c2a_threshold.set("{:g}".format(self.Controller.DEFAULT_ASSIST_THRESHOLD))
        l = ttk.Entry(frame, textvariable=self.c2a_threshold, width=6)
        l.grid(row=1, column=1, sticky="new")
        
        self.c2a_step = tk.StringVar()
        self.c2a_step.set("{:g}".format(self.Controller.DEFAULT_ASSIST_STEP))
        l = ttk.Entry(frame, textvariable=self.c2a_step, width=6)
        l.grid(row=2, column=1, sticky="new")
        
        self.c2a_interval = tk.StringVar()
        self.c2a_interval.set("{:g}".format(self.Controller.DEFAULT_ASSIST_INTERVAL))
        l = ttk.Entry(frame, textvariable=self.c2a_interval, width=6)
        l.grid(row=3, column=1, sticky="new")
        
        l = ttk.Label(frame, text="%")
        l.grid(row=1, column=2, sticky="nw", padx=5)
        l = ttk.Label(frame, text="K")
        l.grid(row=2, column=2, sticky="nw", padx=5)
        l = ttk.Label(frame, text="s")
        l.grid(row=3, column=2, sticky="nw", padx=5)
        
        self.c2a_button_update = ttk.Button(frame, text="update", command=self.c2_update_assist)
        self.c2a_button_update.grid(row=1, column=3, rowspan=3, sticky="nsew", padx=5)
        
        tk.Grid.columnconfigure(frame, 1, weight=1)
        tk.Grid.columnconfigure(frame, 3, weight=1)  
        
    def update_controller(self):
        with self.controller_lock:
            (T1, setp1, rampst1, heater1, T2, setp2, rampst2, heater2) = self.controller.get_status()
        
        # Update Controller entries:
        with self.ui_lock:
            self.c0_T1.configure(text="{:.5g}".format(T1))
            self.c0_T2.configure(text="{:.5g}".format(T2))
            
            self.c0_sp1.configure(text="{:.5g}".format(setp1))
            self.c0_sp2.configure(text="{:.5g}".format(setp2))
            
            if rampst1 > 0:
                self.c0_ramp1.configure(text="On", background="green")
            else:
                self.c0_ramp1.configure(text="Off", background="dim gray")
                
            if rampst2 > 0:
                self.c0_ramp2.configure(text="On", background="green")
            else:
                self.c0_ramp2.configure(text="Off", background="dim gray")
            
            self.c0_heater1.configure(text="{:.5g}".format(heater1))
            self.c0_heater2.configure(text="{:.5g}".format(heater2))
            if heater1 > self.HEATER_LOW:
                self.c0_heater1.configure(background="green")
            else:
                self.c0_heater1.configure(background="dim gray")
            if heater2 > self.HEATER_LOW:
                self.c0_heater2.configure(background="green")
            else:
                self.c0_heater2.configure(background="dim gray")
                
        self.controller_time = time.perf_counter()

    # sorb control functions
    def c1_heater_off(self):
        self.controller.heater_off(1)
        
    def c1_step(self):
        try:
            sp = float(self.c1_sp.get())
            self.controller.step(1, sp)
        except Exception as err:
            self.error_box(err)
            
    def c1_ramp(self):
        try:
            sp = float(self.c1_sp.get())
            r = float(self.c1_rate.get())
            self.controller.ramp(1, sp, r)
        except Exception as err:
            self.error_box(err)
            
    # sample control functions
    def c2_heater_off(self):
        self.controller.heater_off(2)
        
    def c2_step(self):
        try:
            sp = float(self.c2_sp.get())
            self.controller.step(2, sp)
        except Exception as err:
            self.error_box(err)
            
    def c2_ramp(self):
        try:
            sp = float(self.c2_sp.get())
            r = float(self.c2_rate.get())
            self.controller.ramp(2, sp, r)
        except Exception as err:
            self.error_box(err)
            
    def c2_calc_rate(self):
        try:
            sp = float(self.c2_sp.get())
            h = float(self.c2_h.get())
            m = float(self.c2_m.get())
            with self.controller_lock:
                (T1, setp1, rampst1, heater1, T2, setp2, rampst2, heater2) = self.controller.get_status()
            r = abs(sp - T2) / (h*60+m) * self.RATE_MULTIPLIER
            self.c2_rate.set("{:.3g}".format(r))
        except Exception as err:
            self.error_box(err)
            
    def c2_update_assist(self):
        try:
            threshold = float(self.c2_threshold.get())
            step = float(self.c2_step.get())
            interval = float(self.c2_interval.get())
            self.controller.set_assist(threshold=threshold, step=step, interval=interval)
        except Exception as err:
            self.error_box(err)
        

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
            self.lakeshore.set_ramp(loop, 0, self.R_MIN)
            self.lakeshore.set_setp(loop, self.T_MIN)
    
    def step(self, loop, T):
        with self.instrument_lock:
            self.lakeshore.set_ramp(loop, 0, self.R_MIN)
            self.lakeshore.set_setp(loop, T)
    
    def ramp(self, loop, T, r):
        if loop == 1:
            (T1, setp1, rampst1, heater1, T2, setp2, rampst2, heater2) = self.get_status()
            self.step(1, T1)
            with self.instrument_lock:
                self.lakeshore.set_ramp(1, 1, r)
                self.lakeshore.set_setp(1, T)
        elif loop == 2:
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
            if T > T2:
                self.assist_thread = threading.Thread(target=self.ramp_assist)
                self.assist_thread.start()
    
    # Change the parameters for ramping assist
    def set_assist(self, threshold, step, interval):
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
    
     # Temperature cross-over between Si-diode and RuO
    T_RUO_H = 19.
    T_RUO_L = 15.
    
    
    default_params = {
        "R_series1 / Ohm": 'no entry',
        "R_series2 / Ohm": 'no entry',
        "GPIB Lakeshore 340": "{:d}".format(GPIB_LAKESHORE340),
        "sampling interval / s": "0.1"
    }
    param_order = [
        "sampling interval / s",
        "GPIB Lakeshore 340",
        "R_series1 / Ohm",
        "R_series2 / Ohm"
    ]
    
    var_order = VAR_ORDER.copy()    # order of variables
    var_titles = VAR_TITLES.copy()    # matching short names with full titles  = {e.g "H": "$H$ (T / $\mu_0$)"}
    format_strings = VAR_FORMATS.copy()   # Format strings for the variables
    
    plotXYs = [
            [("T_sample", "R1"), ("T_sample", "R2")],
            [("t", "T_sample"), ("t", "T_1K")]
            ]
    
    default_comments = ""
    def __init__(self, params, filename, lockin1, lockin2, magnet):
    
        # Save parameters
        self.lockin1 = lockin1
        self.R_series1 = float(params["R_series1 / Ohm"])
        self.lockin2 = lockin2
        self.R_series2 = float(params["R_series2 / Ohm"])
        self.magnet = magnet
        
        self.measurement_interval = float(params["sampling interval / s"])
        gpib_lakeshore = int(params["GPIB Lakeshore 340"])
        
        # Define the temperature controllers
        self.lakeshore = Lakeshore340(gpib_lakeshore)
        
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
    
    # Calculate the sample temperature from TA and TB
    def calc_Tsample(self, TA, TB):
        if math.isnan(TA) or (TB >= self.T_RUO_H):
            T = TB
        elif math.isnan(TB) or (TB <= self.T_RUO_L):
            T = TA
        else:   # cross-over regime
            T = (TA * (self.T_RUO_H - TB) + TB * (TB - self.T_RUO_L)) / (self.T_RUO_H - self.T_RUO_L)
        
        return T
    
    def measure(self):
        self.current_values["n"] += 1
        t,self.current_values["T_A"] = self.lakeshore.read("A")
        t,self.current_values["T_B"] = self.lakeshore.read("B")
        t,self.current_values["T_sorb"] = self.lakeshore.read("C")
        t,self.current_values["T_1K"] = self.lakeshore.read("D")
        
        self.current_values["t"] = t - self.t0
        
        self.current_values["T_sample"] = self.calc_Tsample(self.current_values["T_A"], self.current_values["T_B"])
        
        t,self.current_values["H"],t = self.magnet.read()
        t,self.current_values["X1"],self.current_values["Y1"],t,t,self.current_values["f1"],self.current_values["Vex1"] = self.lockin1.read()
        t,self.current_values["X2"],self.current_values["Y2"],t,t,self.current_values["f2"],self.current_values["Vex2"] = self.lockin2.read()
        self.current_values["R1"] = self.current_values["X1"] / self.current_values["Vex1"] * self.R_series1
        self.current_values["R2"] = self.current_values["X2"] / self.current_values["Vex2"] * self.R_series2
        
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
        "sampling interval / s": "0.1",
        "R_series1 / Ohm": 'no entry',
        "sens / V": 'no entry',
        "theta / degrees": 'no entry',
        "f / Hz": 'no entry',
        "Vout / V": 'no entry',
        "transformer mode": '0 for False',
        "GPIB Lakeshore 340": "{:d}".format(GPIB_LAKESHORE340),
        "GPIB DMM": "{:d}".format(GPIB_DMM)
    }
    
    param_order = [
        "sampling interval / s",
        "GPIB Lakeshore 340",
        "GPIB DMM",
        "R_series1 / Ohm",
        "sens / V",
        "theta / degrees",
        "f / Hz",
        "Vout / V",
        "transformer mode"]
    
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
        
        gpib_dmm = int(params["GPIB DMM"])
        
        dmm = keithley.Keithley196(gpib_dmm)
        lockin1 = par.PAR124A(dmm, sens=sens, theta=theta, f=f, Vout=Vout, transformer=True)
        lockin2 = fake_lockins.ConstLockin(float("nan"))
        
        magnet = fake_magnets.ConstMagnet()
        
        p = params.copy()
        p["R_series2 / Ohm"] = "0"
        super().__init__(p, filename, lockin1, lockin2, magnet)