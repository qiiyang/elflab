""" Common definitions / whatever shared for all MI-probe related scripts
"""

# Conversion between data names and indices and labels etc.

var_list = ["n", "t", "T", "H", "X", "Y", "t_therm", "t_magnet", "t_lockin", "I_therm", "V_therm", "I_mag", "f", "V_in"]

# Everything in SI

var_desc = {
            "n": "no. of data points",
            "t": "timestamp, absolute, in s",
            "T": "temperature / K",
            "H": "magnetic field, in T",
            "X": "lock-in X reading, in V",
            "Y": "lock-in Y reading, in V",
            "t_therm": "thermometer timestamp, relative",
            "t_magnet": "magnet timestamp, relative",
            "t_lockin": "lock-in timestamp, relative",
            "I_therm": "thermometer current",
            "V_therm": "thermometer voltage",
            "I_mag": "magnet current",
            "f": "lock-in frequency",
            "V_in": "input voltage"
            }
            
var_titles = {
            "n": "n",
            "t": "t / s",
            "T": "T / K",
            "H": "H / T",
            "X": "X / V",
            "Y": "Y / V",
            "t_therm": "t_therm / s",
            "t_magnet": "t_magnet / s",
            "t_lockin": "t_lockin / s",
            "I_therm": "I_therm / A",
            "V_therm": "V_therm / V",
            "I_mag": "I_mag / A",
            "f": "f / Hz",
            "V_in": "V_in / V"
            }
            
var_formats = {
            "n": "{:n}",
            "t": "{:.8f}",
            "T": "{:.10e}",
            "H": "{:.10e}",
            "X": "{:.10e}",
            "Y": "{:.10e}",
            "t_therm": "{:.8f}",
            "t_magnet": "{:.8f}",
            "t_lockin": "{:.8f}",
            "I_therm": "{:.10e}",
            "V_therm": "{:.10e}",
            "I_mag": "{:.10e}",
            "f": "{:.10e}",
            "V_in": "{:.10e}",
            }
            
var_init = {
            "n": 0,
            "t": 0.,
            "T": 0.,
            "H": 0.,
            "X": 0.,
            "Y": 0.,
            "t_therm": 0.,
            "t_magnet": 0.,
            "t_lockin": 0.,
            "I_therm": 0.,
            "V_therm": 0.,
            "I_mag": 0.,
            "f": 0.,
            "V_in": 0.,
            }
            
            