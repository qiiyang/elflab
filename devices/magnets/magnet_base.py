from elflab.devices.device_base import DeviceBase

class MagnetBase(DeviceBase):    
    def __init__(self, address):
        pass
        
    def connect(self):
        pass
    
    def read_field(self):   # returns (t, H/Tesla)
        pass

        