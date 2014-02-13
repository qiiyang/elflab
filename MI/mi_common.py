""" Common definitions / whatever shared for all MI-probe related scripts
"""

# Conversion between data names and indices and labels etc.

dataIndices = { "n": 0,     # data point index
                "t": 1,     # time stamp in s
                "T": 2,     # temperature in K
                "H": 3,     # magnetic field in T
                "X": 4,     # lock-in X in V
                "dX": 5,    # error of X in V
                "Y": 6,     # lock-in Y in V
                "dX": 7,    # error of Y in V
                "I_therm": 8,   # thermometer current
                "V_therm": 9   # thermometer voltage
                }

indicesData = { 0: "n",     # data point index
                1: "t",     # time stamp in s
                2: "T",     # temperature in K
                3: "H",     # magnetic field in T
                4: "X",     # lock-in X in V
                5: "dX",    # error of X in V
                6: "Y",     # lock-in Y in V
                7: "dX" ,   # error of Y in V
                8: "I_therm",   # thermometer current
                9: "V_therm"   # thermometer voltage
                }                
                
dataLabels = { "n": "n",     # data point index
                "t": r"$t$ (s)",     # time stamp in s
                "T": r"$T$ (K)",     # temperature in K
                "H": r"$H$ (T / $\mu_0$)",     # magnetic field in T
                "X": r"$X$ (V)",     # lock-in X in V
                "dX": r"$\Delta{}X (V)",    # error of X in V
                "Y": r"$Y$ (V)",     # lock-in Y in V
                "dY": r"$\Delta{}Y (V)",    # error of Y in V
                "I_therm": r"$I_{therm}$",   # thermometer current
                "V_therm": r"$V_{therm}$"   # thermometer voltage
                }