# Constants

NOTES = """
sample: EuS11 / Al2O3(0001)

Lock-In: SR830
Pre-amplifier: SR554 buffer on

time constant = 10ms
filter = 24db
normal reserve

Couple: AC
ground: ground

expansion: none

phase = 0
sine-out = 5V
Resistor in series: 10.4kOhms
=> I_in ~ 481uA

Thermometer: Lakeshore Si-Diode
Thermometer Current = 10uA
"""

save_path = r"D:\Dropbox\work\MI_data"
filename = r"EuS11_fscan_8K"

THERMOMETER_CALI = r"D:\Dropbox\codes\elflab\devices\thermometers\calibrations\qi_dt01_raw.csv"

SAMPLING_INTERVAL = 0.05
PLOT_LISTEN = 0.01
PLOT_REFRESH = 1.0

# Frequency scan parameters
F_MIN = 10e3
F_MAX = 102e3
F_STEP = 0.1e3

PLOT_VARS = [
            [("f", "X"), ("f", "T")],
            [("f", "Y"), ("t", "f")]
            ]

from elflab.devices.dmms import keithley
from elflab.devices.thermometers import lakeshore
from elflab.devices.lockins import stanford
from elflab.devices.magnets import fake_magnets
            
import time
import os.path
from elflab import galileo
from elflab.dataloggers import csvlogger
import mi_common as mi


class MI_fscan(mi.MI_JustMeasure):
    title = "Mutual Inductance: Scaning over f"
    
    def __init__(self, thermometer, magnet, lockin, logfilename, f_min, f_max, f_step):
        self.f_min = f_min
        self.f_max = f_max
        self.f_step = f_step
        super(MI_fscan, self).__init__(thermometer, magnet, lockin, logfilename)
    
    def sequence(self):
        while True:
            f = self.f_min
            while f <= self.f_max:
                yield self.lockin.setf(f)
                f += self.f_step
            while f >= self.f_min:
                yield self.lockin.setf(f)
                f -= self.f_step
        
# The main procedure
if __name__ == '__main__':        
    print("starting.......")
    
    timestring = time.strftime("%Y%m%d_%H.%M.%S")
    logfilename = os.path.join(save_path, "{0}_{1}.csv".format(timestring, filename))
    notesfilename = os.path.join(save_path, "{0}_{1}_notes.txt".format(timestring, filename))
        
    dmm = keithley.Keithley2000(15)
    thermometer = lakeshore.SiDiode(dmm, THERMOMETER_CALI)
    lockin = stanford.SR830(30)
    
    magnet = fake_magnets.ConstMagnet()
    
    experiment = MI_fscan(thermometer, magnet, lockin, logfilename, F_MIN, F_MAX, F_STEP)
    
    with open(notesfilename, "w") as notesfile:
        notesfile.write("experiment: \"{}\"\n".format(experiment.title))
        notesfile.write("Local time (YYYY/MM/DD, HH:MM:SS): {}\n".format(time.strftime("%Y/%m/%d, %H:%M:%S")))
        notesfile.write(NOTES)
        notesfile.write("thermometer calibration file: \"{}\".\n".format(THERMOMETER_CALI))
    
    gali = galileo.Galileo(experiment, SAMPLING_INTERVAL, PLOT_VARS, plot_refresh_interval=PLOT_REFRESH, plot_listen_interval=PLOT_LISTEN)
    
    gali.start()