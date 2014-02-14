# Measure Once, with no synchronisation at all

import time

def measure(buffer, therm, magnet, lockin): 
         # (data buffer, objects of the instruments)
    buffer["t"] = time.perf_count()
    (buffer["I_therm"], buffer["V_therm"], buffer["T"]) = therm.read()
    (buffer["I_mag"], buffer["H"]) = magnet.read()
    (buffer["X"], buffer["Y"]) = lockin.read()
    return buffer