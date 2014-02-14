""" DMMs Base class """

from ..device_base import DeviceBase

class DMMBase(DeviceBase):   
    def read(self):
        return 0.

        