######################################################################################################
# A prototype GUI
######################################################################################################
import time
import os
import multiprocessing

import elflab.abstracts

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter.scrolledtext import ScrolledText

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
        
        self.buttonStop = ttk.Button(self.mainFrame, text="stop", command=self.kernel.stop)
        self.buttonStop.grid(column=1, row=2, sticky=tk.W)
        
        self.buttonQuit = ttk.Button(self.mainFrame, text="quit", command=self.quit)
        self.buttonQuit.grid(column=1, row=4, sticky=tk.W)
        
        self.buttonPlot = ttk.Button(self.mainFrame, text="plot", command=self.kernel.plot)
        self.buttonPlot.grid(column=2, row=1, sticky=tk.W)
        
        self.buttonAutoOn = ttk.Button(self.mainFrame, text="autoscale: on", command=self.kernel.autoscaleOn)
        self.buttonAutoOn.grid(column=2, row=2, sticky=tk.W)
        
        self.buttonAutoOff = ttk.Button(self.mainFrame, text="autoscale: off", command=self.kernel.autoscaleOff)
        self.buttonAutoOff.grid(column=2, row=3, sticky=tk.W)
        
        self.buttonClear = ttk.Button(self.mainFrame, text="clear plots", command=self.kernel.clearPlot)
        self.buttonClear.grid(column=2, row=4, sticky=tk.W)
        
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
    # CONSTANTS
    DEFAULT_FOLDER = r"d:\data_dump"
    DEFAULT_FN = r"datalog"
    PATH_LENGTH = 50
    FN_LENGTH = 20
    
    VAR_FORMAT = "{}{}={:.5g};     "
    PARAM_LENGTH = 15
    
    UI_REFRESH = 0.1   # Update ui every #seconds
    STATUS_REFRESH = 1.0    # Update the status frame every # seconds
    CONTROLLER_REFRESH = 5.0   # Update controller status every #seconds
    
    # default values to pass on to the kernel
    DEFAULT_PLOT_REFRESH_INTERVAL = 0.5     # Interval between plot refreshes in s
    DEFAULT_PLOT_LISTEN_INTERVAL = 0.05    # Interval between listening events in s
    
    def __init__(self, Kernel, Experiment, Controller=None):
        # 0=stoped, 1=running, 2=paused
        self.state = 0
        
        # saving arguments
        self.Kernel = Kernel
        self.Experiment = Experiment
        self.Controller = Controller
        
        self.params = Experiment.default_params.copy()
        self.var_titles = Experiment.var_titles
        
        # declare objects
        self.kernel = None
        self.experiment = None
        self.controller = None
        
        # setting gui root
        self.root = tk.Tk()
        try:
            title = "{}: {}".format(Kernel.title, Experiment.title)
        except Exception:
            title = "Undefined Kernel Title"
        self.root.title(title)
        
        # Declare containers
        self.folder_str = self.DEFAULT_FOLDER
        self.filename_var = tk.StringVar()
        self.filename_var.set(self.DEFAULT_FN)
        
        # Declare other variables
        self.controller_time = self.status_time = time.perf_counter()

        self.instrument_lock = multiprocessing.Lock()
        self.data_lock = multiprocessing.Lock()
        self.ui_lock = multiprocessing.Lock()
        self.controller_lock = multiprocessing.Lock()
        
        
        self.kernel_kwargs = {
            "plot_refresh_interval": self.DEFAULT_PLOT_REFRESH_INTERVAL,
            "plot_listen_interval": self.DEFAULT_PLOT_LISTEN_INTERVAL,
            "data_lock": self.data_lock,
            "instrument_lock": self.instrument_lock
        }
        
        self.controller_kwargs = {
            "data_lock": self.data_lock,
            "instrument_lock": self.instrument_lock,
            "controller_lock": self.controller_lock
        }
        
        # Define styles
        style = ttk.Style()
        style.configure("RedFG.TButton", foreground="red")
        style.configure("GreenBG.TButton", background="green")

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
        
        self.commentFrame = ttk.LabelFrame(self.mainFrame, text="comments")
        self.commentFrame.grid(row=1, column=1, sticky="nwe")
        
        self.commandFrame = ttk.LabelFrame(self.mainFrame, text="Program Control")
        self.commandFrame.grid(row=1, column=2, sticky="nwe")
        
        self.controlFrame = ttk.LabelFrame(self.mainFrame, text="experiment control")
        self.controlFrame.grid(row=2, column=1, columnspan=2, sticky="nwe")
        
        self.statusFrame = ttk.LabelFrame(self.mainFrame, text="status")
        self.statusFrame.grid(row=3, column=1, columnspan=2, sticky="nwe")
        
            # File options
        self.file_label1 = ttk.Label(self.fileFrame, text="file name: \"(time stamp)_")
        self.file_label1.pack(side=tk.LEFT)
        self.file_entry = ttk.Entry(self.fileFrame, width=self.FN_LENGTH, textvariable=self.filename_var)
        self.file_entry.pack(side=tk.LEFT)
        self.file_label2 = ttk.Label(self.fileFrame, text=".dat\"")
        self.file_label2.pack(side=tk.LEFT)
        
        self.folder_button = ttk.Button(self.fileFrame, text="directory", command=self.change_folder)
        self.folder_button.pack(side=tk.LEFT, padx=(32,0))
        
        self.folder_label = ttk.Label(self.fileFrame, width=self.PATH_LENGTH, justify=tk.LEFT)
        self.folder_label.pack(side=tk.LEFT)
        self.set_folder(self.folder_str)
        
            # Parameters
        self.param_vars = {}
        r = 0
        for par in self.params:
            w = ttk.Label(self.paramFrame, text=par)
            w.grid(column=0, row=r, sticky="nw")
            self.param_vars[par] = tk.StringVar()
            self.param_vars[par].set(self.params[par])
            w = ttk.Entry(self.paramFrame, width=self.PARAM_LENGTH, textvariable=self.param_vars[par])
            w.grid(column=0, row=r+1, sticky="nw", pady=(0,3))
            r += 2
        
            # Comments box
        self.comment_button = ttk.Button(self.commentFrame, text="update", command=self.update_comment, state="disabled")
        self.comment_button.grid(row=0, column=0, sticky="nw")
        self.comment_box = ScrolledText(self.commentFrame, width=40, height=10)
        self.comment_box.insert(0., Experiment.default_comments)
        self.comment_box.grid(row=1, column=0, sticky="nw")
        
            # commands
        self.kernelLabel = ttk.Label(self.commandFrame, text="stopped", justify=tk.CENTER, background="", relief="groove")
        self.kernelLabel.grid(column=1, row=1, sticky="ew")
        
        self.buttonStart = ttk.Button(self.commandFrame, text="start", command=self.start_kernel)
        self.buttonStart.grid(column=1, row=2, sticky="ew")
            
        self.buttonPause = ttk.Button(self.commandFrame, text="pause", command=self.pause_kernel, state="disabled")
        self.buttonPause.grid(column=1, row=3, sticky="ew")
        
        self.buttonQuit = ttk.Button(self.commandFrame, text="quit", style="RedFG.TButton", command=self.quit)
        self.buttonQuit.grid(column=1, row=4, sticky="ew")
        
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
        
        # Status
        st = ""
        for var in self.var_titles:
            st = "{}{}={};     ".format(st, self.var_titles[var], "not available")
        self.statusLabel = ttk.Label(self.statusFrame, text=st, justify=tk.LEFT, foreground="blue")
        self.statusLabel.grid(sticky="nw")
        
    def quit(self):
        if self.kernel is not None:
            self.kernel.quit()
        if self.controller is not None:
            self.controller.terminate()
        self.root.quit()
    
    def start(self):
        # Calculate the wrapping length for status
        self.mainFrame.update()
        w = self.commentFrame.winfo_reqwidth() + self.commandFrame.winfo_reqwidth() - 1
        self.statusLabel.configure(wraplength=w)
        
        # Update Frames and Define the scrolling
        self.mainFrame.update()
        self.mainCanvas.config(width=self.mainFrame.winfo_reqwidth(), height=self.mainFrame.winfo_reqheight(), scrollregion = (0, 0, self.mainFrame.winfo_reqwidth(), self.mainFrame.winfo_reqheight()))
        
        self.ybar.config(command=self.mainCanvas.yview)
        self.xbar.config(command=self.mainCanvas.xview)
        self.mainCanvas.config(xscrollcommand=self.xbar.set, yscrollcommand=self.ybar.set)
        
        # Starting a controller instance
        if self.Controller is not None:
            self.controller = self.Controller(kernel=None, **self.controller_kwargs)
        
        # Start the gui
        self.update_interface()
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

    def update_comment(self):
        with open(self.comments_file, "a") as f:)
            f.write("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++\n")
            f.write("\nUPDATE:\n")
            f.write("Local time (YYYY/MM/DD, HH:MM:SS): {}\n".format(time.strftime("%Y/%m/%d, %H:%M:%S")))
            f.write("____________________________________________________________\n")
            t = self.comment_box.get(0.0, tk.END)
            f.write(t)     
        
    # Refresh UI according to the state
    def set_ui_state(self, state):
        with self.ui_lock:
            self.state = state
            # Disable / enable widgets
            if state > 0:
                s1 = "disable"
                s2 = "normal"
                self.buttonStart.configure(text="stop", style="GreenBG.TButton", command=self.stop_kernel)
            else:
                s1 = "normal"
                s2 = "disable"
                self.buttonStart.configure(text="start", style="TButton", command=self.start_kernel)
            for child in self.fileFrame.winfo_children():
                child.configure(state=s1)
            for child in self.paramFrame.winfo_children():
                child.configure(state=s1)
            
            self.comment_button.configure(state=s2)
            self.buttonPause.configure(state=s2)
            self.buttonPlot.configure(state=s2)
            self.buttonAutoOn.configure(state=s2)
            self.buttonAutoOff.configure(state=s2)
            self.buttonClear.configure(state=s2)
            
            # update state label
            if state == 0:
                self.kernelLabel.configure(text="stopped", background="", foreground="")
            elif state == 1:
                self.kernelLabel.configure(text="running", background="green", foreground="white")
                self.buttonPause.configure(text="pause", style="TButton", command=self.pause_kernel)
            else:
                self.kernelLabel.configure(text="paused", background="yellow", foreground="")
                self.buttonPause.configure(text="resume", style="GreenBG.TButton", command=self.resume_kernel)
                
        
    def start_kernel(self):
        try:            
            # Read parameters
            for par in self.params:
                self.params[par] = self.param_vars[par].get()
            if self.kernel is not None:
                self.kernel.quit()
            
            # Parse file names, and create the comments file
            filename = self.filename_var.get()
            timestring = time.strftime("%Y.%m.%d_%H.%M.%S")
            self.data_file = os.path.join(self.folder_str, "{0}_{1}.dat".format(timestring, filename))
            self.comments_file = os.path.join(self.folder_str, "{0}_{1}_comments.txt".format(timestring, filename))
            
            with open(self.comments_file, "w") as f:
                f.write("experiment: \"{}\"\n".format(self.Experiment.title))
                f.write("Local time (YYYY/MM/DD, HH:MM:SS): {}\n".format(time.strftime("%Y/%m/%d, %H:%M:%S")))
                f.write("____________________________________________________________\n")
                t = self.comment_box.get(0.0, tk.END)
                f.write(t)
                f.write("\n\nParameters:\n")
                for par in self.params:
                    f.write("   {} = {}\n".format(par, self.params[par]))
                
                           
            # Start the experiment and the kernel
            self.experiment = self.Experiment(params=self.params, filename=self.data_file)
            self.kernel = self.Kernel(self.experiment, **self.kernel_kwargs)
            self.kernel.start()
            
            # Restart a controller instance
            if self.controller is not None:
                self.controller.terminate()
            if self.Controller is not None:
                self.controller = self.Controller(kernel=self.kernel, **self.controller_kwargs)
        except Exception as err:
            messagebox.showerror("Cannot start kernel", "    An error has occurred, try checking the parameter values.\nerror code:\n    {}".format(err))
        else:
            with self.ui_lock:
                self.buttonStart.configure(text="stop", style="GreenBG.TButton", command=self.stop_kernel)
        
    def stop_kernel(self):
        self.kernel.stop()
        
    def pause_kernel(self):
        self.kernel.pause()
        with self.ui_lock:
            self.buttonPause.configure(text="resume", style="GreenBG.TButton", command=self.resume_kernel)
    
    def resume_kernel(self):
        self.kernel.resume()
        with self.ui_lock:
            self.buttonPause.configure(text="pause", style="TButton", command=self.pause_kernel)
        
    def kernel_plot(self):
        self.kernel.plot()
        
    def kernel_autoscaleOn(self):
        self.kernel.autoscaleOn()
        
    def kernel_autoscaleOff(self):
        self.kernel.autoscaleOff()
        
    def kernel_clearPlot(self):
        self.kernel.clearPlot()
    
    # book keeping: update the controller status
    def update_controller(self):
        pass
    
    def update_status(self):
        st = ""
        with self.data_lock:
            for var in self.var_titles:
                st = self.VAR_FORMAT.format(st, self.var_titles[var], self.kernel.current_values[var])
        
        with self.ui_lock:
            self.statusLabel.configure(text=st)
        
    # book keeping: update the interface
    def update_interface(self):
        with self.ui_lock:
            if (self.kernel is None) or self.kernel.flag_stop or self.kernel.flag_quit:
                new_state = 0
            elif self.kernel.flag_pause:
                new_state = 2
            else:
                new_state = 1
        if new_state != self.state:
            self.set_ui_state(new_state)
        
        t = time.perf_counter()
        
        if (self.state > 0) and (t - self.status_time > self.STATUS_REFRESH):
            self.status_time = t
            self.update_status()
            
        if t - self.controller_time > self.CONTROLLER_REFRESH:
            self.controller_time = t
            self.update_controller()
            
        self.root.after(round(self.UI_REFRESH*1000.), self.update_interface)