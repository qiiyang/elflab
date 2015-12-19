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
        
        self.mainFrame = ttk.Frame(self.root, padding="3 3 12 12")
        self.mainFrame.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))
        self.mainFrame.columnconfigure(0, weight=1)
        self.mainFrame.rowconfigure(0, weight=1)
        
        self.buttonPause = ttk.Button(self.mainFrame, text="pause", command=self.kernel.pause)
        self.buttonPause.grid(column=1, row=1, sticky=tk.W)
        
        self.buttonResume = ttk.Button(self.mainFrame, text="resume", command=self.kernel.resume)
        self.buttonResume.grid(column=1, row=2, sticky=tk.W)
        
        self.buttonStop = ttk.Button(self.mainFrame, text="stop", command=self.kernel.stop)
        self.buttonStop.grid(column=1, row=3, sticky=tk.W)
        
        self.buttonPlot = ttk.Button(self.mainFrame, text="plot", command=self.kernel.plot)
        self.buttonPlot.grid(column=2, row=1, sticky=tk.W)
        
        self.buttonAutoOn = ttk.Button(self.mainFrame, text="autoscale: on", command=self.kernel.autoscaleOn)
        self.buttonAutoOn.grid(column=2, row=2, sticky=tk.W)
        
        self.buttonAutoOff = ttk.Button(self.mainFrame, text="autoscale: off", command=self.kernel.autoscaleOff)
        self.buttonAutoOff.grid(column=2, row=3, sticky=tk.W)
        
        self.buttonClear = ttk.Button(self.mainFrame, text="clear plots", command=self.kernel.clearPlot)
        self.buttonClear.grid(column=2, row=4, sticky=tk.W)
        
        self.buttonQuit = ttk.Button(self.mainFrame, text="quit", command=self.quit)
        self.buttonQuit.grid(column=1, row=5, sticky=tk.W)
        
        for child in self.mainFrame.winfo_children():
            child.grid_configure(padx=5, pady=5)
        
    def quit(self):
        self.kernel.quit()
        self.root.quit()
    
    def start(self):
        self.kernel.start()        
        self.root.mainloop()
        
        
# A GUI for a generic experiment, with file, comments and a controller panel
class GenericGUI(elflab.abstracts.UIBase):
    def __init__(self, kernel):
    
        # default values
        self.folder = r"C:\Data"
        self.filename = r"logfile"
        
        # setting gui
        self.kernel = kernel
        self.root = tk.Tk()
        try:
            title = kernel.title
        except Exception:
            title = "Undefined Kernel Title"
        self.root.title(title)

        # Define the scrolling frame
        self.ybar = ttk.Scrollbar(self.root, orient=tk.VERTICAL)
        self.ybar.grid(row=0, column=1, sticky="ns")
        
        self.xbar = ttk.Scrollbar(self.root, orient=tk.HORIZONTAL)
        self.xbar.grid(row=1, column=0, sticky="we")
        
        self.mainCanvas = tk.Canvas(self.root)
        self.mainCanvas.grid(row=0, column=0, sticky="nswe")
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        self.mainFrame = ttk.Frame(self.mainCanvas)
        self.mainCanvas.create_window((0, 0), window=self.mainFrame, anchor=tk.NW)
        
        # Contents - label frames
        self.fileFrame = ttk.LabelFrame(self.mainFrame, text="file")
        self.fileFrame.grid(row=0, column=0, columnspan=2, sticky="we") 
        w = tk.Label(self.fileFrame, text="text")
        w.pack()
        
        self.commentFrame = ttk.LabelFrame(self.mainFrame, text="comments")
        self.commentFrame.grid(row=1, column=0, sticky="we")
        w = tk.Label(self.commentFrame, text="text")
        w.pack()
        
        self.commandFrame = ttk.LabelFrame(self.mainFrame, text="commands")
        self.commandFrame.grid(row=1, column=1, sticky="we")
        w = tk.Label(self.commandFrame, text="text")
        w.pack()
        
        self.controlFrame = ttk.Frame(self.mainFrame)
        self.controlFrame.grid(row=2, column=0, columnspan=2, sticky="we")
        w = tk.Label(self.controlFrame, text="experiment controls")
        w.pack()
        
        self.statusFrame = ttk.LabelFrame(self.mainFrame, text="status")
        self.statusFrame.grid(row=3, column=0, columnspan=2, sticky="we")
        w = tk.Label(self.statusFrame, text="text")
        w.pack()
        
        
        # Define the scrolling
        self.mainFrame.update()
        self.mainCanvas.config(width=self.mainFrame.winfo_reqwidth(), height=self.mainFrame.winfo_reqheight(), scrollregion = (0, 0, self.mainFrame.winfo_reqwidth(), self.mainFrame.winfo_reqheight()))
        self.ybar.config(command=self.mainCanvas.yview)
        self.xbar.config(command=self.mainCanvas.xview)
        self.mainCanvas.config(xscrollcommand=self.xbar.set, yscrollcommand=self.ybar.set)
        
    def quit(self):
        #self.kernel.quit()
        self.root.quit()
    
    def start(self):
        #self.kernel.start()        
        self.root.mainloop()