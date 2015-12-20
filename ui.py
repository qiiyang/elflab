######################################################################################################
# A prototype GUI
######################################################################################################
import elflab.abstracts

import tkinter as tk
from tkinter import ttk, filedialog

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
    PATH_LENGTH = 60
    FN_LENGTH = 20
    def __init__(self, kernel):
        
        # setting gui root
        self.kernel = kernel
        self.root = tk.Tk()
        try:
            title = kernel.title
        except Exception:
            title = "Undefined Kernel Title"
        self.root.title(title)
        
        # Declare containers
        self.folder_str = r"C:/data"
        self.filename_var = tk.StringVar()
        self.filename_var.set(r"logfile")
        
        # Define styles
        style = ttk.Style()
        style.configure("Red.TButton", foreground="red")
        style.configure("Gold.TButton", foreground="gold")
        style.configure("Pressed.TButton", background="green")

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
        
        # Contents - layout frames
        self.fileFrame = ttk.LabelFrame(self.mainFrame, text="Data File")
        self.fileFrame.grid(row=0, column=0, columnspan=3, sticky="we")
        
        self.paramFrame = ttk.LabelFrame(self.mainFrame, text="Parameters")
        self.paramFrame.grid(row=1, column=0, rowspan=3, sticky="nswe")
        w = ttk.Label(self.paramFrame, text="text")
        w.pack()
        
        self.commentFrame = ttk.LabelFrame(self.mainFrame, text="comments")
        self.commentFrame.grid(row=1, column=1, sticky="nwe")
        
        self.commandFrame = ttk.LabelFrame(self.mainFrame, text="commands")
        self.commandFrame.grid(row=1, column=2, sticky="nwe")
        
        self.controlFrame = ttk.LabelFrame(self.mainFrame, text="experiment control")
        self.controlFrame.grid(row=2, column=1, columnspan=2, sticky="nwe")
        
        self.statusFrame = ttk.LabelFrame(self.mainFrame, text="status")
        self.statusFrame.grid(row=3, column=1, columnspan=2, sticky="nwe")
        
            # File options
        self.file_label1 = ttk.Label(self.fileFrame, text="file name: \"[time stamp]_")
        self.file_label1.pack(side=tk.LEFT)
        self.file_entry = ttk.Entry(self.fileFrame, width=self.FN_LENGTH, textvariable=self.filename_var)
        self.file_entry.pack(side=tk.LEFT)
        self.file_label2 = ttk.Label(self.fileFrame, text=".csv\"")
        self.file_label2.pack(side=tk.LEFT)
        
        self.folder_button = ttk.Button(self.fileFrame, text="directory", command=self.change_folder)
        self.folder_button.pack(side=tk.LEFT, padx=(32,0))
        
        self.folder_label = ttk.Label(self.fileFrame, width=self.PATH_LENGTH, justify=tk.LEFT)
        self.folder_label.pack(side=tk.LEFT)
        self.set_folder(self.folder_str)
        
            # Comments box
        self.comment_box = tk.Text(self.commentFrame, width=40, height=10)
        self.comment_box.pack()
        
            # commands        
        self.buttonStart = ttk.Button(self.commandFrame, text="start", command=self.start_kernel)
        self.buttonStart.grid(column=1, row=1, sticky="ew")
            
        self.buttonPause = ttk.Button(self.commandFrame, text="pause", command=self.pause_kernel, state="disabled")
        self.buttonPause.grid(column=1, row=2, sticky="ew")
        
        self.buttonResume = ttk.Button(self.commandFrame, text="resume", command=self.resume_kernel, state="disabled")
        self.buttonResume.grid(column=1, row=3, sticky="ew")
        
        self.buttonQuit = ttk.Button(self.commandFrame, text="quit", style="Red.TButton", command=self.quit)
        self.buttonQuit.grid(column=1, row=5, sticky="ew")
        
        self.buttonPlot = ttk.Button(self.commandFrame, text="plot", command=self.kernel_plot, state="disabled")
        self.buttonPlot.grid(column=2, row=1, sticky="ew")
        
        self.buttonAutoOn = ttk.Button(self.commandFrame, text="autoscale: on", command=self.kernel_autoscaleOn, state="disabled")
        self.buttonAutoOn.grid(column=2, row=2, sticky="ew")
        
        self.buttonAutoOff = ttk.Button(self.commandFrame, text="autoscale: off", command=self.kernel_autoscaleOff, state="disabled")
        self.buttonAutoOff.grid(column=2, row=3, sticky="ew")
        
        self.buttonClear = ttk.Button(self.commandFrame, text="clear plots", command=self.kernel_clearPlot, state="disabled")
        self.buttonClear.grid(column=2, row=4, sticky="ew")
        
        for child in self.commandFrame.winfo_children():
            child.grid_configure(padx=5, pady=5)
        

        
    def quit(self):
        #self.kernel.quit()
        self.root.quit()
    
    def start(self):
        # Update Frames and Define the scrolling
        self.mainFrame.update()
        self.mainCanvas.config(width=self.mainFrame.winfo_reqwidth(), height=self.mainFrame.winfo_reqheight(), scrollregion = (0, 0, self.mainFrame.winfo_reqwidth(), self.mainFrame.winfo_reqheight()))
        self.ybar.config(command=self.mainCanvas.yview)
        self.xbar.config(command=self.mainCanvas.xview)
        self.mainCanvas.config(xscrollcommand=self.xbar.set, yscrollcommand=self.ybar.set)        
        self.root.mainloop()
        
    def change_folder(self):
        folder = filedialog.askdirectory()
        self.set_folder(folder)
        
    def set_folder(self, folder):
        self.folder_str = folder
        l = len(folder)
        if l <= self.PATH_LENGTH:
            folder_txt = folder
        else:
            folder_txt = "...{}".format(self.folder_str[-self.PATH_LENGTH+3:l])
        self.folder_label.config(text=folder_txt)

    # Disable / Enable interface states between run and stop
    def set_run_state(self, running):
        if running:
            s1 = "disable"
            s2 = "normal"
        else:
            s1 = "normal"
            s2 = "disable"
        for child in self.fileFrame.winfo_children():
            child.configure(state=s1)
        for child in self.commentFrame.winfo_children():
            child.configure(state=s1)
        for child in self.paramFrame.winfo_children():
            child.configure(state=s1)
            
        for child in self.controlFrame.winfo_children():
            child.configure(state=s1)
        self.buttonPause.configure(state=s2)
        self.buttonResume.configure(state=s2)
        self.buttonPlot.configure(state=s2)
        self.buttonAutoOn.configure(state=s2)
        self.buttonAutoOff.configure(state=s2)
        self.buttonClear.configure(state=s2)
        
    def start_kernel(self):
        self.set_run_state(True)
        self.buttonStart.configure(text="stop", style="Pressed.TButton", command=self.stop_kernel)
        
    def stop_kernel(self):
        self.set_run_state(False)
        self.buttonStart.configure(text="start", style="TButton", command=self.start_kernel)
        
    def pause_kernel(self):
        pass
        
    def resume_kernel(self):
        pass
        
    def kernel_plot(self):
        pass
        
    def kernel_autoscaleOn(self):
        pass
        
    def kernel_autoscaleOff(self):
        pass
        
    def kernel_clearPlot(self):
        pass