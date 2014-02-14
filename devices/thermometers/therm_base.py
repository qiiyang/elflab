""" Thermometer base """

from ..device_base import DeviceBase

class ThermBase(DeviceBase):
    """ returns 0. as I, V, T """
    
    def read(self):
        return (0., 0., 0.)

        