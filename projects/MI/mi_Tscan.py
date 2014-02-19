# Constants

NOTES = """
sample: EuS11 / Al2O3(0001)

Lock-In: SR830
Pre-amplifier: SR554, buffer on
time constant = 10ms
filter = 24db
normal reserve
phase = 0
f = 45.40kHz
sine-out = 1.04V
Resistor in series: 10.4kOhms
=> I_in ~ 100uA

Thermometer: Lakeshore Si-Diode
Thermometer Current = 10uA
"""

TITLE = "MI RT test"
save_path = r"D:\Dropbox\work\MI_data"
filename = r"EuS11_Tscan"

THERMOMETER_CALI = r"D:\Dropbox\codes\elflab\devices\thermometers\calibrations\qi_dt01_raw.csv"

SAMPLING_INTERVAL = 0.05
PLOT_LISTEN = 0.01
PLOT_REFRESH = 1.0

SENS_RANGE = (0.1, 0.8)

PLOT_VARS = [
            [("T", "X"), ("t", "T")],
            [("T", "Y"), ("t", "n")]
            ]

from elflab.devices.dmms import keithley
from elflab.devices.thermometers import lakeshore
from elflab.devices.lockins import stanford
from elflab.devices.magnets import fake_magnets
            
import time
import os.path
from elflab import abstracts, galileo
from elflab.dataloggers import csvlogger
import mi_common as mi

class MIMeasurer(abstracts.Measurer):
    def __init__(self, thermometer, magnet, lockin):
        self.currentValues = mi.var_init.copy()
        self.varTitles = mi.var_titles
        
        self.thermometer = thermometer
        self.magnet = magnet
        self.lockin = lockin
               
    def measure(self):
        self.currentValues["n"] += 1
        self.currentValues["t"] = self.t0 + time.perf_counter()
        (self.currentValues["t_therm"], self.currentValues["T"], self.currentValues["I_therm"], self.currentValues["V_therm"]) = self.thermometer.read()
        (self.currentValues["t_mag"], self.currentValues["H"], self.currentValues["I_mag"]) = self.magnet.read()
        (self.currentValues["t_lockin"], self.currentValues["X"], self.currentValues["Y"], R, theta, self.currentValues["f"], self.currentValues["V_in"]) = self.lockin.read()
        
    def start(self):
        thermometer.connect()
        lockin.connect()
        lockin.setAutoSens(*SENS_RANGE)
        
        self.n = 0
        self.t0 = time.time()
        time.perf_counter()
        
    def finish(self):
        del self.thermometer
        del self.magnet
        del self.lockin
        
        
# The main procedure
if __name__ == '__main__':        
    print("starting.......")
    
    timestring = time.strftime("%Y%m%d_%H.%M.%S")
    logfilename = os.path.join(save_path, "{0}_{1}.csv".format(timestring, filename))
    notesfilename = os.path.join(save_path, "{0}_{1}_notes.txt".format(timestring, filename))
    
    with open(notesfilename, "w") as notesfile:
        notesfile.write("Local time (YYYY/MM/DD, HH:MM:SS): {}\n".format(time.strftime("%Y/%m/%d, %H:%M:%S")))
        notesfile.write(NOTES)
        notesfile.write("thermometer calibration file: \"{}\".\n".format(THERMOMETER_CALI))
        
    dmm = keithley.Keithley2000(15)
    thermometer = lakeshore.SiDiode(dmm, THERMOMETER_CALI)
    lockin = stanford.SR830(30)
    
    magnet = fake_magnets.ConstMagnet()
    
    measurer = MIMeasurer(thermometer, magnet, lockin)
    
    logger = csvlogger.Logger(logfilename, mi.var_list, mi.var_titles, mi.var_formats)
    
    experiment = abstracts.ML_Experiment(TITLE, measurer, logger)
    
    gali = galileo.Galileo(experiment, SAMPLING_INTERVAL, PLOT_VARS, plot_refresh_interval=PLOT_REFRESH, plot_listen_interval=PLOT_LISTEN)
    
    gali.start()