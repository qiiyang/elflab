""" Common definitions / whatever shared for all MI-probe related scripts
"""

# Conversion between data names and indices and labels etc.

dataIndices = { "n": 0,     # data point index
                "t": 1,     # time stamp in s
                "T": 2,     # temperature in K
                "f": 3,     # Frequency in Hz
                "H": 4,     # magnetic field in T
                "X": 5,     # lock-in X in V
                "dX": 6,    # error of X in V
                "Y": 7,     # lock-in Y in V
                "dX": 8,    # error of Y in V
                "I_therm": 9,   # thermometer current
                "V_therm": 10,   # thermometer voltage
                "I_mag": 11     # magnet current
                }

indicesData = [ "n",     # data point index
                "t",     # time stamp in s
                "T",     # temperature in K
                "H",     # magnetic field in T
                "f",     # Frequency in Hz
                "X",     # lock-in X in V
                "dX",    # error of X in V
                "Y",     # lock-in Y in V
                "dX" ,   # error of Y in V
                "I_therm",   # thermometer current
                "V_therm",   # thermometer voltage
                "I_mag"
                ]                
                
dataLabels = { "n": "n",     # data point index
                "t": r"$t$ (s)",     # time stamp in s
                "T": r"$T$ (K)",     # temperature in K
                "H": r"$H$ (T / $\mu_0$)",     # magnetic field in T
                "f": r"$f$ (Hz)",     # Frequency in Hz
                "X": r"$X$ (V)",     # lock-in X in V
                "dX": r"$\Delta{}X (V)",    # error of X in V
                "Y": r"$Y$ (V)",     # lock-in Y in V
                "dY": r"$\Delta{}Y (V)",    # error of Y in V
                "I_therm": r"$I_{therm}$",   # thermometer current
                "V_therm": r"$V_{therm}$",   # thermometer voltage
                "I_mag": r"$I_{mag}$"     # magnet current
                }

# Templates for initialise a data point                
initialData = { "n": 0,     # data point index
                "t": 0.,     # time stamp in s
                "T": 0.,     # temperature in K
                "H": 0.,     # magnetic field in T
                "f": 0.,     # Frequency in Hz
                "X": 0.,     # lock-in X in V
                "dX": 0.,    # error of X in V
                "Y": 0.,     # lock-in Y in V
                "dX": 0.,    # error of Y in V
                "I_therm": 0.,   # thermometer current
                "V_therm": 0.,   # thermometer voltage
                "I_mag": 0.     # magnet current
                }