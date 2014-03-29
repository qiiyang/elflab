# Constants

NOTES = """
sample: MgB2 / Al2O3 (r) 11-05-01B

Lock-In: SR830
Pre-amplifier: SR554 buffer on

time constant = 100ms
filter = 24db
normal noise reserve

Couple: DC
ground: ground

expansion: 

phase = 0
f=13.594kHz
sine-out = 2.08V
Resistor in series: 10.4kOhms
=> I_in ~ 100uA

Thermometer: Lakeshore Si-Diode
Thermometer Current = 10uA

Grounded lockin, dewar and preamp together to AC earth
"""

save_path = r"D:\Dropbox\work\2014, MI\data"
filename = r"YBCO_Tscan_13.6kHz_no_preamp_cooling"

THERMOMETER_CALI = r"D:\Dropbox\codes\elflab\devices\thermometers\calibrations\qi_dt01_raw.csv"

SAMPLING_INTERVAL = 0.05
PLOT_LISTEN = 0.01
PLOT_REFRESH = 1.0

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
from elflab import galileo
from elflab.dataloggers import csvlogger
import mi_common as mi


class MI_Tscan(mi.MI_JustMeasure):
    title = "Mutual Inductance: Measuring against T"

        
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
    
    experiment = MI_Tscan(thermometer, magnet, lockin, logfilename)
    
    with open(notesfilename, "w") as notesfile:
        notesfile.write("experiment: \"{}\"\n".format(experiment.title))
        notesfile.write("Local time (YYYY/MM/DD, HH:MM:SS): {}\n".format(time.strftime("%Y/%m/%d, %H:%M:%S")))
        notesfile.write(NOTES)
        notesfile.write("thermometer calibration file: \"{}\".\n".format(THERMOMETER_CALI))
    
    gali = galileo.Galileo(experiment, SAMPLING_INTERVAL, PLOT_VARS, plot_refresh_interval=PLOT_REFRESH, plot_listen_interval=PLOT_LISTEN)
    
    gali.start()