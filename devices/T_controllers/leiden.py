""" Reading temperatures from Leiden Temperature Controller VI """
import win32com.client
import time
from elflab.devices.T_controllers.T_controller_base import TControllerBase

# Copied from Leiden code examples
class LVApp:
    def __init__(self, AppName, ViName):
        self.App = win32com.client.Dispatch(AppName)
        self.Vi = self.App.GetViReference(ViName)

    # Reading data from VI's is straight forward
    def GetData(self, ControlName):
        return self.Vi.GetControlValue(ControlName)
        
    def SetData(self, ControlName, ControlData, Async = False):
        if type(ControlData) in (tuple, list):
            self.Vi.SetControlValue('SetControl', (ControlName, '', ControlData))
        else:
            self.Vi.SetControlValue('SetControl', (ControlName, ControlData, [[], []]))
        if not Async:
            while self.Vi.GetControlValue('SetControl')[0] != '': time.sleep(0.1)

# Actual implementation of the temperature controller
class LeidenTC(TControllerBase): 
    # Default read function, returns (t, T) of the specified channel
    def __init__(self, address):    # address = path to the executable
        self.address = address
        self.connected = True
    
    def connect(self):
        pass
    
    def read(self, ch):     # return (t, T, R) for the specified channel
        TC = LVApp("DRTempControl.Application", address)
        reading = TC.GetData("T{}".format(ch))
        try:
            T = float(reading) / 1.e3
        except ValueError:
            T = float("nan")
        reading = TC.GetData("R{}".format(ch))
        try:
            R = float(reading)
        except ValueError:
            R = float("nan")
        t = time.perf_counter()
        return (t, T, R)
        
        


        