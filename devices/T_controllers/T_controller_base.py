""" Thermometer base """

class TControllerBase:
    # Default read function, returns (t, T) of the specified channel
    def read(self, ch):     
        raise Exception("temperature controller not implemented")
        
        


        