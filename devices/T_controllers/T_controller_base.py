""" Thermometer base """

class TControllerBase:
    # Default read function, returns (t, T) of the specified channel
    def connect(self):     
        raise Exception("temperature controller not implemented")
    def read(self, ch):     
        raise Exception("temperature controller not implemented")
        
        


        