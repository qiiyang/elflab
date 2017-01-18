from elflab.devices.thermometers.therm_base import ThermBase

class RTD(ThermBase):

    # Conversion function from resistance (Ohm) to temperature (Kelvin), using the European standard curve
    def ohm_to_kelvin(self, R):
        T = 273.15 -245.19 + R*(2.5293+R*(-0.066046+R*(0.0040422+R*(-0.0000020697))))/(1+R*(-0.025422+R*(0.0016883+R*(-0.0000013601))))
        return T
    
    # Use a lock-in amplifier to read the resistance of the RTD
    def __init__(self, lockin, R_series):
        self.lockin = lockin
        self.R_series = R_series
        
    
    def connect(self):
        self.lockin.connect()
        
    def read(self):
        t, X, _, _, _, _, Vout = self.lockin.read()
        Itherm = Vout / self.R_series
        T = self.ohm_to_kelvin(X / Itherm)
        
        return (t, T, Itherm, X)
        
        