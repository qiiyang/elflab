""" Thermometer base """

class ThermBase:
    # Default read finction, returns (t, I, V, T)
    def read(self):     
        raise Exception("thermometer not implemented")
        
    # Only returns T
    def readT(self):
        (t, I, V, T) = self.read()
        return T
        
    # Interpolate T from the calibration
    def IVtoT(self, I, V):
        raise Exception("thermometer not implemented")
        
        


        