""" Oxford Magnet Power Supplies """
import visa
import time
from .magnet_base import MagnetBase

import tkinter as tk
from tkinter import ttk

class IPS120_10(MagnetBase):
    def __init__(self, address):
        self.address = address
        
        self.connected = False
        self.H = float('nan')
        self.I = float('nan')
        
    def connect(self):
        rm = visa.ResourceManager()
        self.gpib = rm.open_resource("GPIB::{:n}".format(self.address), read_termination='\r', write_termination='\r')
        self.gpib.write("Q4")
        print("        Oxford IPS 120-10 magnet power supply connected, GPIB={:n}.".format(self.address))        
        self.connected = True
    
    def read(self): # returns (t, H/Tesla, I_magnet/A)
        stat = str(self.gpib.query("X"))
        while len(stat) != 15:
            stat = str(self.gpib.query("X"))
        
        if (stat[8] == '0') or (stat[8] == '2'):    # persistent switch closed
            # use persistent values
            err = True  # error flag for detecting GPIB error
            while err:
                try:
                    s = str(self.gpib.query("R18")).strip("Rr")
                    self.H = float(s)
                except:
                    pass
                else:
                    err = False
            err = True  # error flag for detecting GPIB error
            while err:
                try:
                    s = str(self.gpib.query("R16")).strip("Rr")
                    self.I = float(s)
                except:
                    pass
                else:
                    err = False
        else:   # persistent switch open or not present
            # use demand / measured values
            err = True  # error flag for detecting GPIB error
            while err:
                try:
                    s = str(self.gpib.query("R7")).strip("Rr")  # Demand field
                    self.H = float(s)
                except:
                    pass
                else:
                    err = False
            err = True  # error flag for detecting GPIB error
            while err:
                try:
                    s = str(self.gpib.query("R2")).strip("Rr")  # Measured Current
                    self.I = float(s)
                except:
                    pass
                else:
                    err = False
            
        return (time.perf_counter(), self.H, self.I)
        
    def get_gui(self, master):
        ENTRY_LENGTH = 10
        
        gui_frame = ttk.LabelFrame(master, text="Oxford IPS 120-10")
        
        setpoint = tk.StringVar()
        setpoint_box = ttk.Entry(gui_frame, width=ENTRY_LENGTH, textvariable=setpoint)
        setpoint_box.grid(row=0, column=0, columnspan=4, sticky="new")
        
        setpoint_button = ttk.Button(gui_frame, text="setpoint / T", command=None)
        setpoint_button.grid(row=0, column=4, columnspan=2, sticky="new")
        
        setrate = tk.StringVar()
        setrate_box = ttk.Entry(gui_frame, width=ENTRY_LENGTH, textvariable=setrate)
        setrate_box.grid(row=1, column=0, columnspan=4, sticky="new")
        
        setrate_button = ttk.Button(gui_frame, text="setpoint / T", command=None)
        setrate_button.grid(row=1, column=4, columnspan=2, sticky="new")
        
        hold_button = ttk.Button(gui_frame, text="hold", command=None)
        hold_button.grid(row=2, column=0, sticky="new")
        
        to0_button = ttk.Button(gui_frame, text="to 0", command=None)
        to0_button.grid(row=2, column=1, sticky="new")
        
        toset_button = ttk.Button(gui_frame, text="to set", command=None)
        toset_button.grid(row=2, column=2, sticky="new")
        
        heateron_button = ttk.Button(gui_frame, text="heater on", command=None)
        heateron_button.grid(row=2, column=3, sticky="new")
        
        heateroff_button = ttk.Button(gui_frame, text="heater off", command=None)
        heateroff_button.grid(row=2, column=4, sticky="new")
        
        remote_button = ttk.Button(gui_frame, text="remote", command=None)
        remote_button.grid(row=2, column=5, sticky="new")
            
        return gui_frame
        

        