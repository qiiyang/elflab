from elflab.devices.device_base import DeviceBase

class MagnetBase(DeviceBase):    
    def __init__(self, address):
        raise Exception("Magnet power supply driver not implemented!!!")
        
    def connect(self):
        raise Exception("Magnet power supply driver not implemented!!!")
    
    def read(self):   # returns (t, H/Tesla, I_magnet/A)
        raise Exception("Magnet power supply driver not implemented!!!")

        