######################################################################################################
# A prototype GUI
######################################################################################################
import elflab.abstracts

import tkinter as tk
import tkinter.ttk as ttk

class Prototype(elflab.abstracts.UIBase):
    def __init__(self, gali):
        self.gali = gali
        
    def start(self):
        self.root = tk.Tk()
        self.root.title("Galileo")
        
        self.mainframe = ttk.Frame(self.root, padding="3 3 12 12")
        self.mainframe.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))
        self.mainframe.columnconfigure(0, weight=1)
        self.mainframe.rowconfigure(0, weight=1)
        
        self.buttonPause = ttk.Button(self.mainframe, text="pause")
        self.buttonPause.grid(column=1, row=1, sticky=tk.W)
        
        self.buttonResume = ttk.Button(self.mainframe, text="resume")
        self.buttonResume.grid(column=1, row=2, sticky=tk.W)
        
        self.buttonStop = ttk.Button(self.mainframe, text="stop")
        self.buttonStop.grid(column=1, row=3, sticky=tk.W)
        
        self.buttonQuit = ttk.Button(self.mainframe, text="quit")
        self.buttonQuit.grid(column=1, row=4, sticky=tk.W)
        
        self.buttonPlot = ttk.Button(self.mainframe, text="plot")
        self.buttonPlot.grid(column=2, row=1, sticky=tk.W)
        
        self.buttonAutoOn = ttk.Button(self.mainframe, text="autoscale: on")
        self.buttonAutoOn.grid(column=2, row=2, sticky=tk.W)
        
        self.buttonAutoOff = ttk.Button(self.mainframe, text="autoscale: off")
        self.buttonAutoOff.grid(column=2, row=3, sticky=tk.W)
        
        for child in self.mainframe.winfo_children():
            child.grid_configure(padx=5, pady=5)
        
        self.root.mainloop()