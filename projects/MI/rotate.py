
import mi_common as mi
import numpy as np
import matplotlib.pyplot as plt


if __name__ == '__main__': 
    data=mi.loadfile(r"D:\Dropbox\work\2014, MI\data\20140220\20140220_11.26.54_MgB2_Tscan_13.6kHz_cooling.csv")
    Ts=data["T"]
    Rs=data["R"]
    ths=data["theta"]
    Xs = Rs * np.cos((ths + 180. + 76.) * np.pi / 180.)
    Ys = Rs * np.sin((ths + 180.+ 76.) * np.pi / 180.)

    plt.plot(Ts, Xs, "bx", Ts, Ys, "r+")

    plt.legend(("Re($V_{out}$)", "Im($V_{out}$)"))
    plt.xlabel("$T$ / K")
    plt.ylabel("$V_{out}$ / V")

    plt.show()