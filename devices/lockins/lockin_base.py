""" Lockin base class """

from ..device_base import DeviceBase

class LockinBase(DeviceBase):  
    def readXY(self):       # Returns X, Y in volts
        return (0., 0.)

        