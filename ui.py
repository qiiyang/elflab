######################################################################################################
# A prototype GUI
######################################################################################################
import elflab.abstracts

import tkinter as tk
import tkinter.ttk as ttk

class Text:
    def __init__(self, kernel):
        self.kernel = kernel
        # Map commands to methods
        self.valid_commands = {
                    "help": self.kernel.help, "h": self.kernel.help,
                    "pause": self.kernel.pause, "p": self.kernel.pause,
                    "resume": self.kernel.resume, "r": self.kernel.resume,
                    "stop": self.kernel.stop,
                    "quit": self.kernel.quit,
                    "plot": self.kernel.plot,
                    "autoscale on": self.kernel.autoscaleOn, "+a": self.kernel.autoscaleOn,
                    "autoscale off": self.kernel.autoscaleOff, "-a": self.kernel.autoscaleOff,
                    "clear plot": self.kernel.clearPlot,
                    "": self.kernel.prompt
                    }
        
    def start(self):
        # Print help infomation
        self.kernel.help()
        # Start the measurements
        self.kernel.start()
        # User interaction: command parsing etc.
        while not self.kernel.flag_quit:
            command = input().strip().lower()
            if command in self.valid_commands:
                self.valid_commands[command]()
            else:
                self.kernel.wrongCommand(command)                              

# A prototype gui, which emulates the text ui
class PrototypeGUI(elflab.abstracts.UIBase):
    def __init__(self, kernel):
        self.kernel = kernel
        self.root = tk.Tk()
        self.root.title("Galileo")
        
        self.mainframe = ttk.Frame(self.root, padding="3 3 12 12")
        self.mainframe.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))
        self.mainframe.columnconfigure(0, weight=1)
        self.mainframe.rowconfigure(0, weight=1)
        
        self.buttonPause = ttk.Button(self.mainframe, text="pause", command=self.kernel.pause)
        self.buttonPause.grid(column=1, row=1, sticky=tk.W)
        
        self.buttonResume = ttk.Button(self.mainframe, text="resume", command=self.kernel.resume)
        self.buttonResume.grid(column=1, row=2, sticky=tk.W)
        
        self.buttonStop = ttk.Button(self.mainframe, text="stop", command=self.kernel.stop)
        self.buttonStop.grid(column=1, row=3, sticky=tk.W)
        
        self.buttonPlot = ttk.Button(self.mainframe, text="plot", command=self.kernel.plot)
        self.buttonPlot.grid(column=2, row=1, sticky=tk.W)
        
        self.buttonAutoOn = ttk.Button(self.mainframe, text="autoscale: on", command=self.kernel.autoscaleOn)
        self.buttonAutoOn.grid(column=2, row=2, sticky=tk.W)
        
        self.buttonAutoOff = ttk.Button(self.mainframe, text="autoscale: off", command=self.kernel.autoscaleOff)
        self.buttonAutoOff.grid(column=2, row=3, sticky=tk.W)
        
        self.buttonClear = ttk.Button(self.mainframe, text="clear plots", command=self.kernel.clearPlot)
        self.buttonClear.grid(column=2, row=4, sticky=tk.W)
        
        self.buttonQuit = ttk.Button(self.mainframe, text="quit", command=self.quit)
        self.buttonQuit.grid(column=1, row=5, sticky=tk.W)
        
        for child in self.mainframe.winfo_children():
            child.grid_configure(padx=5, pady=5)
        
    def quit(self):
        self.root.quit()
        self.kernel.quit()
    
    def start(self):
        self.kernel.start()        
        self.root.mainloop()