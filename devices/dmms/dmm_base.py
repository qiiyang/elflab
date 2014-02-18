""" DMMs Base class """

from ..device_base import DeviceBase

class DMMBase(DeviceBase):   
    def read(self):     # Returns (t, current reading in SI)
        raise Expection("DMM not implemented")

        